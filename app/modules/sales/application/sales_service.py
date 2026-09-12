from datetime import date, datetime, timezone
import uuid
from typing import Sequence
from sqlalchemy.orm import Session
from app.modules.inventory.infrastructure.inventory_repository import InventoryRepository
from app.modules.inventory.infrastructure.models import InventoryMovement, MovementType
from app.modules.products.domain.exceptions import ProductNotFoundError
from app.modules.products.infrastructure.models import Product, ProductStatus
from app.modules.sales.domain.exceptions import (
    InsufficientDisplayStockError,
    InsufficientPaymentError,
    InvalidSaleStateError,
    RefundExceedsOriginalError,
    SaleNotFoundError,
)
from app.modules.sales.domain.schemas import SaleCreateRequest, SaleRefundRequest
from app.modules.sales.infrastructure.models import PaymentMethod, Sale, SaleItem, SaleRefund, SaleRefundItem, SaleStatus
from app.modules.sales.infrastructure.sales_repository import SalesRepository


class SalesService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SalesRepository(db)
        self.inv_repo = InventoryRepository(db)

    def create_sale(
        self,
        payload: SaleCreateRequest,
        cashier_id: uuid.UUID,
    ) -> Sale:
        # 1. Idempotency Check
        if payload.idempotency_key:
            existing = self.repo.get_by_idempotency_key(payload.idempotency_key)
            if existing:
                return existing

        # 2. Validate Cart Items, Stock Availability, and Calculate Total
        calculated_total = 0.0
        validated_items: list[tuple[Product, int, float]] = []

        for item_in in payload.items:
            prod = self.db.get(Product, item_in.product_id)
            if not prod or prod.status != ProductStatus.ACTIVE:
                raise ProductNotFoundError(str(item_in.product_id))

            unit_price = item_in.unit_price if item_in.unit_price is not None else float(prod.selling_price)
            subtotal = unit_price * item_in.quantity
            calculated_total += subtotal

            # Lock inventory row and check display stock
            inv = self.inv_repo.get_by_product_id(prod.id, lock=True)
            available_disp = inv.display_quantity if inv else 0

            if available_disp < item_in.quantity:
                raise InsufficientDisplayStockError(
                    product_name=prod.name,
                    available=available_disp,
                    requested=item_in.quantity,
                )

            validated_items.append((prod, item_in.quantity, unit_price))

        # 3. Validate Cash Payment
        if payload.cash_paid < calculated_total:
            raise InsufficientPaymentError(
                cash_paid=payload.cash_paid,
                total_amount=calculated_total,
            )

        cash_change = payload.cash_paid - calculated_total
        receipt_num = self.repo.generate_receipt_number()

        # 4. Create Sale Record
        sale = Sale(
            id=uuid.uuid4(),
            receipt_number=receipt_num,
            business_date=date.today(),
            cashier_id=cashier_id,
            total_amount=calculated_total,
            payment_method=payload.payment_method,
            cash_paid=payload.cash_paid,
            cash_change=cash_change,
            status=SaleStatus.COMPLETED,
            idempotency_key=payload.idempotency_key,
        )

        # 5. Process Items, Deduct Display Stock, and Insert Movements
        for prod, qty, price in validated_items:
            item_subtotal = price * qty
            sale_item = SaleItem(
                id=uuid.uuid4(),
                sale_id=sale.id,
                product_id=prod.id,
                quantity=qty,
                unit_price=price,
                subtotal=item_subtotal,
            )
            sale.items.append(sale_item)

            # Deduct DISPLAY quantity
            inv = self.inv_repo.get_by_product_id(prod.id, lock=True)
            inv.display_quantity -= qty
            self.inv_repo.update_inventory(inv)

            # Insert SALE movement log
            movement = InventoryMovement(
                id=uuid.uuid4(),
                product_id=prod.id,
                movement_type=MovementType.SALE,
                quantity=qty,
                from_location="DISPLAY",
                to_location=None,
                reference_type="SALE",
                reference_id=sale.id,
                actor_id=cashier_id,
            )
            self.inv_repo.create_movement(movement)

        self.repo.create_sale(sale)
        self.db.commit()
        self.db.refresh(sale)
        return sale

    def list_sales(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        cashier_id: uuid.UUID | None = None,
        status: SaleStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Sale], int]:
        return self.repo.list_sales(
            start_date=start_date,
            end_date=end_date,
            cashier_id=cashier_id,
            status=status,
            skip=skip,
            limit=limit,
        )

    def get_sale_by_id(self, sale_id: uuid.UUID) -> Sale:
        sale = self.repo.get_sale_by_id(sale_id)
        if not sale:
            raise SaleNotFoundError(str(sale_id))
        return sale

    def get_sale_by_receipt(self, receipt_number: str) -> Sale:
        sale = self.repo.get_sale_by_receipt(receipt_number)
        if not sale:
            raise SaleNotFoundError(receipt_number)
        return sale

    def void_sale(self, sale_id: uuid.UUID, actor_id: uuid.UUID) -> Sale:
        sale = self.repo.get_sale_by_id(sale_id, lock=True)
        if not sale:
            raise SaleNotFoundError(str(sale_id))

        if sale.status != SaleStatus.COMPLETED:
            raise InvalidSaleStateError(sale.status.value, "void")

        sale.status = SaleStatus.VOIDED

        # Restore DISPLAY stock for all sale items
        for item in sale.items:
            inv = self.inv_repo.get_by_product_id(item.product_id, lock=True)
            if inv:
                inv.display_quantity += item.quantity
                self.inv_repo.update_inventory(inv)

            movement = InventoryMovement(
                id=uuid.uuid4(),
                product_id=item.product_id,
                movement_type=MovementType.RETURN,
                quantity=item.quantity,
                from_location=None,
                to_location="DISPLAY",
                reference_type="VOID",
                reference_id=sale.id,
                actor_id=actor_id,
            )
            self.inv_repo.create_movement(movement)

        self.repo.update_sale(sale)
        self.db.commit()
        self.db.refresh(sale)
        return sale

    def refund_sale(
        self,
        sale_id: uuid.UUID,
        payload: SaleRefundRequest,
        processed_by_id: uuid.UUID,
    ) -> SaleRefund:
        sale = self.repo.get_sale_by_id(sale_id, lock=True)
        if not sale:
            raise SaleNotFoundError(str(sale_id))

        if sale.status not in [SaleStatus.COMPLETED, SaleStatus.PARTIALLY_REFUNDED]:
            raise InvalidSaleStateError(sale.status.value, "refund")

        refund_num = self.repo.generate_refund_number()
        total_refund_amount = 0.0

        refund = SaleRefund(
            id=uuid.uuid4(),
            sale_id=sale.id,
            refund_number=refund_num,
            refund_amount=0.0,
            reason=payload.reason,
            processed_by_id=processed_by_id,
        )

        sale_items_dict = {item.id: item for item in sale.items}

        for item_in in payload.items:
            sale_item = sale_items_dict.get(item_in.sale_item_id)
            if not sale_item:
                raise RefundExceedsOriginalError(f"Sale item '{item_in.sale_item_id}' does not belong to sale '{sale_id}'.")

            if item_in.quantity > sale_item.quantity:
                raise RefundExceedsOriginalError(
                    f"Refund quantity ({item_in.quantity}) exceeds purchased quantity ({sale_item.quantity})."
                )

            item_refund_amt = float(sale_item.unit_price) * item_in.quantity
            total_refund_amount += item_refund_amt

            refund_item = SaleRefundItem(
                id=uuid.uuid4(),
                refund_id=refund.id,
                sale_item_id=sale_item.id,
                quantity=item_in.quantity,
                refund_amount=item_refund_amt,
            )
            refund.items.append(refund_item)

            # Restore DISPLAY stock
            inv = self.inv_repo.get_by_product_id(sale_item.product_id, lock=True)
            if inv:
                inv.display_quantity += item_in.quantity
                self.inv_repo.update_inventory(inv)

            movement = InventoryMovement(
                id=uuid.uuid4(),
                product_id=sale_item.product_id,
                movement_type=MovementType.RETURN,
                quantity=item_in.quantity,
                from_location=None,
                to_location="DISPLAY",
                reference_type="REFUND",
                reference_id=refund.id,
                actor_id=processed_by_id,
            )
            self.inv_repo.create_movement(movement)

        refund.refund_amount = total_refund_amount
        self.repo.create_refund(refund)

        # Update sale status
        sale.status = SaleStatus.REFUNDED
        self.repo.update_sale(sale)

        self.db.commit()
        self.db.refresh(refund)
        return refund
