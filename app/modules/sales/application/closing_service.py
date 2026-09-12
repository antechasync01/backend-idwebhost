from datetime import date
import uuid
from typing import Sequence
from sqlalchemy.orm import Session
from app.modules.inventory.infrastructure.inventory_repository import InventoryRepository
from app.modules.products.infrastructure.models import Product
from app.modules.sales.domain.exceptions import (
    AlreadyClosedError,
    DailyClosingNotFoundError,
    InvalidClosingStateError,
)
from app.modules.sales.domain.schemas import (
    CashClosingRequest,
    CashClosingSummaryResponse,
    InventoryClosingRequest,
)
from app.modules.sales.infrastructure.models import (
    CashClosing,
    DailyClosing,
    DailyClosingStatus,
    InventoryClosing,
    InventoryClosingItem,
    InventoryClosingVarianceStatus,
)
from app.modules.sales.infrastructure.sales_repository import SalesRepository


class ClosingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SalesRepository(db)
        self.inv_repo = InventoryRepository(db)

    def get_cash_closing_summary(
        self,
        business_date: date,
        opening_cash: float = 0.0,
    ) -> CashClosingSummaryResponse:
        cash_sales = self.repo.calculate_today_cash_sales(business_date)
        refunds = self.repo.calculate_today_refunds(business_date)
        expected_cash = opening_cash + cash_sales - refunds

        return CashClosingSummaryResponse(
            business_date=business_date,
            opening_cash=opening_cash,
            cash_sales=cash_sales,
            refunds=refunds,
            cash_adjustment=0.0,
            expected_cash=expected_cash,
        )

    def submit_cash_closing(
        self,
        payload: CashClosingRequest,
        cashier_id: uuid.UUID,
        business_date: date | None = None,
    ) -> CashClosing:
        target_date = business_date or date.today()
        daily_closing = self.repo.get_or_create_daily_closing(target_date)

        if daily_closing.status == DailyClosingStatus.FINALIZED:
            raise AlreadyClosedError("Daily store closing", str(target_date))

        if daily_closing.cash_closing is not None:
            raise AlreadyClosedError("Cash closing", str(target_date))

        cash_sales = self.repo.calculate_today_cash_sales(target_date)
        refunds = self.repo.calculate_today_refunds(target_date)
        expected_cash = payload.opening_cash + cash_sales - refunds + payload.cash_adjustment
        variance = payload.actual_cash - expected_cash

        cash_closing = CashClosing(
            id=uuid.uuid4(),
            daily_closing_id=daily_closing.id,
            cashier_id=cashier_id,
            opening_cash=payload.opening_cash,
            cash_sales=cash_sales,
            refunds=refunds,
            cash_adjustment=payload.cash_adjustment,
            adjustment_notes=payload.adjustment_notes,
            expected_cash=expected_cash,
            actual_cash=payload.actual_cash,
            variance=variance,
            notes=payload.notes,
        )

        self.repo.create_cash_closing(cash_closing)

        # Update DailyClosing status
        if daily_closing.status == DailyClosingStatus.OPEN:
            daily_closing.status = DailyClosingStatus.CASH_CLOSED
        elif daily_closing.status == DailyClosingStatus.INVENTORY_CLOSED:
            # Both closing components completed
            daily_closing.status = DailyClosingStatus.CASH_CLOSED

        self.repo.update_daily_closing(daily_closing)
        self.db.commit()
        self.db.refresh(cash_closing)
        return cash_closing

    def submit_inventory_closing(
        self,
        payload: InventoryClosingRequest,
        business_date: date | None = None,
    ) -> InventoryClosing:
        target_date = business_date or date.today()
        daily_closing = self.repo.get_or_create_daily_closing(target_date)

        if daily_closing.status == DailyClosingStatus.FINALIZED:
            raise AlreadyClosedError("Daily store closing", str(target_date))

        if daily_closing.inventory_closing is not None:
            raise AlreadyClosedError("Inventory closing", str(target_date))

        overall_status = InventoryClosingVarianceStatus.MATCHED
        items_objs: list[InventoryClosingItem] = []

        for item_in in payload.items:
            inv = self.inv_repo.get_by_product_id(item_in.product_id)
            exp_disp = inv.display_quantity if inv else 0
            exp_on_hand = inv.on_hand_quantity if inv else 0

            disp_var = item_in.physical_display_quantity - exp_disp
            on_hand_var = item_in.physical_on_hand_quantity - exp_on_hand

            item_status = (
                InventoryClosingVarianceStatus.MATCHED
                if (disp_var == 0 and on_hand_var == 0)
                else InventoryClosingVarianceStatus.NEEDS_REVIEW
            )

            if item_status == InventoryClosingVarianceStatus.NEEDS_REVIEW:
                overall_status = InventoryClosingVarianceStatus.NEEDS_REVIEW

            item_obj = InventoryClosingItem(
                id=uuid.uuid4(),
                product_id=item_in.product_id,
                opening_display_quantity=exp_disp,
                opening_on_hand_quantity=exp_on_hand,
                receiving_quantity=0,
                sales_quantity=0,
                adjustment_quantity=0,
                return_quantity=0,
                other_movement_quantity=0,
                expected_display_quantity=exp_disp,
                expected_on_hand_quantity=exp_on_hand,
                physical_display_quantity=item_in.physical_display_quantity,
                physical_on_hand_quantity=item_in.physical_on_hand_quantity,
                display_variance=disp_var,
                on_hand_variance=on_hand_var,
                status=item_status,
            )
            items_objs.append(item_obj)

        inv_closing = InventoryClosing(
            id=uuid.uuid4(),
            daily_closing_id=daily_closing.id,
            status=overall_status,
            notes=payload.notes,
        )
        inv_closing.items.extend(items_objs)

        self.repo.create_inventory_closing(inv_closing)

        if daily_closing.status in [DailyClosingStatus.OPEN, DailyClosingStatus.CASH_CLOSED]:
            daily_closing.status = DailyClosingStatus.INVENTORY_CLOSED

        self.repo.update_daily_closing(daily_closing)
        self.db.commit()
        self.db.refresh(inv_closing)
        return inv_closing

    def finalize_daily_closing(
        self,
        closed_by_id: uuid.UUID,
        business_date: date | None = None,
    ) -> DailyClosing:
        target_date = business_date or date.today()
        daily_closing = self.repo.get_daily_closing_by_date(target_date)

        if not daily_closing:
            raise DailyClosingNotFoundError(str(target_date))

        if daily_closing.status == DailyClosingStatus.FINALIZED:
            raise AlreadyClosedError("Daily store closing", str(target_date))

        daily_closing.status = DailyClosingStatus.FINALIZED
        daily_closing.closed_by_id = closed_by_id

        self.repo.update_daily_closing(daily_closing)
        self.db.commit()
        self.db.refresh(daily_closing)
        return daily_closing

    def list_daily_closings(self, skip: int = 0, limit: int = 50) -> tuple[Sequence[DailyClosing], int]:
        return self.repo.list_daily_closings(skip=skip, limit=limit)
