import uuid
from typing import Sequence
from sqlalchemy.orm import Session
from app.modules.inventory.infrastructure.inventory_repository import InventoryRepository
from app.modules.inventory.infrastructure.models import Inventory, InventoryMovement, MovementType
from app.modules.products.domain.exceptions import ProductNotFoundError
from app.modules.products.infrastructure.models import Product
from app.modules.users.infrastructure.models import User
from app.modules.warehouse.domain.exceptions import (
    InvalidReceivingItemError,
    InvalidReceivingStateError,
    ReceivingNotFoundError,
    WarehouseRequestNotFoundError,
)
from app.modules.warehouse.domain.schemas import (
    ReceivingCreate,
    ReceivingReview,
    ReceivingUpdate,
    WarehouseRequestCreate,
    WarehouseRequestReview,
)
from app.modules.warehouse.infrastructure.models import Receiving, ReceivingItem, ReceivingStatus, WarehouseRequest, WarehouseRequestStatus
from app.modules.warehouse.infrastructure.warehouse_repository import WarehouseRepository


class WarehouseService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = WarehouseRepository(db)
        self.inv_repo = InventoryRepository(db)

    # ---------------- Receiving Workflow Operations ----------------
    def submit_receiving(
        self,
        payload: ReceivingCreate,
        submitted_by: User,
    ) -> Receiving:
        if not payload.items:
            raise InvalidReceivingItemError("At least one receiving item is required.")

        # 1. Validate all products exist
        for item in payload.items:
            prod = self.db.get(Product, item.product_id)
            if not prod:
                raise ProductNotFoundError(str(item.product_id))

        # 2. Determine initial status based on role (Auto-approve for Admin/Owner)
        user_role_code = submitted_by.role_rel.code if submitted_by.role_rel else ""
        auto_approve = user_role_code in ["WAREHOUSE_ADMIN", "OWNER"]

        rec_status = ReceivingStatus.APPROVED if auto_approve else ReceivingStatus.PENDING
        receiving_num = self.repo.generate_receiving_number()

        receiving = Receiving(
            id=uuid.uuid4(),
            receiving_number=receiving_num,
            supplier_id=payload.supplier_id,
            status=rec_status,
            submitted_by_id=submitted_by.id,
            reviewed_by_id=submitted_by.id if auto_approve else None,
            notes=payload.notes,
        )

        for item_in in payload.items:
            rec_item = ReceivingItem(
                id=uuid.uuid4(),
                receiving_id=receiving.id,
                product_id=item_in.product_id,
                quantity_received=item_in.quantity_received,
                unit_cost=item_in.unit_cost,
            )
            receiving.items.append(rec_item)

        self.repo.create_receiving(receiving)

        # 3. If auto-approved, immediately increment ON_HAND inventory & log movement
        if auto_approve:
            self._apply_receiving_to_inventory(receiving=receiving, actor_id=submitted_by.id)

        self.db.commit()
        self.db.refresh(receiving)
        return receiving

    def list_receivings(
        self,
        status: ReceivingStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Receiving], int]:
        return self.repo.list_receivings(status=status, skip=skip, limit=limit)

    def get_receiving_by_id(self, receiving_id: uuid.UUID) -> Receiving:
        rec = self.repo.get_receiving_by_id(receiving_id)
        if not rec:
            raise ReceivingNotFoundError(str(receiving_id))
        return rec

    def approve_receiving(
        self,
        receiving_id: uuid.UUID,
        payload: ReceivingReview,
        reviewer: User,
    ) -> Receiving:
        rec = self.repo.get_receiving_by_id(receiving_id, lock=True)
        if not rec:
            raise ReceivingNotFoundError(str(receiving_id))

        if rec.status not in [ReceivingStatus.PENDING, ReceivingStatus.CORRECTION_REQUESTED]:
            raise InvalidReceivingStateError(rec.status.value, "approve")

        rec.status = ReceivingStatus.APPROVED
        rec.reviewed_by_id = reviewer.id
        if payload.review_notes:
            rec.notes = f"{rec.notes or ''}\n[Review Notes]: {payload.review_notes}".strip()

        self.repo.update_receiving(rec)

        # Increment ON_HAND inventory and log movement
        self._apply_receiving_to_inventory(receiving=rec, actor_id=reviewer.id)

        self.db.commit()
        self.db.refresh(rec)
        return rec

    def reject_receiving(
        self,
        receiving_id: uuid.UUID,
        payload: ReceivingReview,
        reviewer: User,
    ) -> Receiving:
        rec = self.repo.get_receiving_by_id(receiving_id, lock=True)
        if not rec:
            raise ReceivingNotFoundError(str(receiving_id))

        if rec.status not in [ReceivingStatus.PENDING, ReceivingStatus.CORRECTION_REQUESTED]:
            raise InvalidReceivingStateError(rec.status.value, "reject")

        rec.status = ReceivingStatus.REJECTED
        rec.reviewed_by_id = reviewer.id
        if payload.review_notes:
            rec.notes = f"{rec.notes or ''}\n[Rejection Notes]: {payload.review_notes}".strip()

        self.repo.update_receiving(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec

    def request_correction(
        self,
        receiving_id: uuid.UUID,
        payload: ReceivingReview,
        reviewer: User,
    ) -> Receiving:
        rec = self.repo.get_receiving_by_id(receiving_id, lock=True)
        if not rec:
            raise ReceivingNotFoundError(str(receiving_id))

        if rec.status != ReceivingStatus.PENDING:
            raise InvalidReceivingStateError(rec.status.value, "request_correction")

        rec.status = ReceivingStatus.CORRECTION_REQUESTED
        rec.reviewed_by_id = reviewer.id
        if payload.review_notes:
            rec.notes = f"{rec.notes or ''}\n[Correction Request]: {payload.review_notes}".strip()

        self.repo.update_receiving(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec

    def _apply_receiving_to_inventory(self, receiving: Receiving, actor_id: uuid.UUID) -> None:
        """Internal helper to increment ON_HAND inventory and insert PURCHASE_RECEIVING movement logs."""
        for item in receiving.items:
            inv = self.inv_repo.get_by_product_id(item.product_id, lock=True)
            if not inv:
                inv = Inventory(
                    id=uuid.uuid4(),
                    product_id=item.product_id,
                    display_quantity=0,
                    on_hand_quantity=item.quantity_received,
                )
                self.db.add(inv)
            else:
                inv.on_hand_quantity += item.quantity_received
                self.inv_repo.update_inventory(inv)

            movement = InventoryMovement(
                id=uuid.uuid4(),
                product_id=item.product_id,
                movement_type=MovementType.PURCHASE_RECEIVING,
                quantity=item.quantity_received,
                from_location=None,
                to_location="ON_HAND",
                reference_type="RECEIVING",
                reference_id=receiving.id,
                actor_id=actor_id,
            )
            self.inv_repo.create_movement(movement)

    # ---------------- Warehouse Requests Operations ----------------
    def submit_warehouse_request(
        self,
        payload: WarehouseRequestCreate,
        requested_by_id: uuid.UUID,
    ) -> WarehouseRequest:
        prod = self.db.get(Product, payload.product_id)
        if not prod:
            raise ProductNotFoundError(str(payload.product_id))

        req = WarehouseRequest(
            id=uuid.uuid4(),
            product_id=payload.product_id,
            requested_quantity=payload.requested_quantity,
            notes=payload.notes,
            status=WarehouseRequestStatus.PENDING,
            requested_by_id=requested_by_id,
        )
        self.repo.create_warehouse_request(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def list_warehouse_requests(
        self,
        status: WarehouseRequestStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[WarehouseRequest], int]:
        return self.repo.list_warehouse_requests(status=status, skip=skip, limit=limit)

    def resolve_warehouse_request(
        self,
        request_id: uuid.UUID,
        payload: WarehouseRequestReview,
        reviewer: User,
    ) -> WarehouseRequest:
        req = self.repo.get_warehouse_request_by_id(request_id)
        if not req:
            raise WarehouseRequestNotFoundError(str(request_id))

        req.status = WarehouseRequestStatus.RESOLVED
        if payload.notes:
            req.notes = f"{req.notes}\n[Resolution Notes]: {payload.notes}".strip()

        self.repo.update_warehouse_request(req)
        self.db.commit()
        self.db.refresh(req)
        return req
