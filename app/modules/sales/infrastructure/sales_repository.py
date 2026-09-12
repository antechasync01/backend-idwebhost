from datetime import date, datetime, timezone
import uuid
from typing import Sequence
from sqlalchemy import Date, func, select
from sqlalchemy.orm import Session
from app.modules.sales.infrastructure.models import (
    CashClosing,
    DailyClosing,
    DailyClosingStatus,
    InventoryClosing,
    InventoryClosingItem,
    Sale,
    SaleItem,
    SaleRefund,
    SaleRefundItem,
    SaleStatus,
)


class SalesRepository:
    def __init__(self, db: Session):
        self.db = db

    def generate_receipt_number(self) -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        prefix = f"INV-{date_str}-"
        count_stmt = select(func.count(Sale.id)).where(Sale.receipt_number.like(f"{prefix}%"))
        count = self.db.scalar(count_stmt) or 0
        seq = count + 1
        return f"{prefix}{seq:04d}"

    def generate_refund_number(self) -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        prefix = f"RFD-{date_str}-"
        count_stmt = select(func.count(SaleRefund.id)).where(SaleRefund.refund_number.like(f"{prefix}%"))
        count = self.db.scalar(count_stmt) or 0
        seq = count + 1
        return f"{prefix}{seq:04d}"

    def get_by_idempotency_key(self, idempotency_key: str) -> Sale | None:
        return self.db.scalar(select(Sale).where(Sale.idempotency_key == idempotency_key))

    def create_sale(self, sale: Sale) -> Sale:
        self.db.add(sale)
        self.db.flush()
        return sale

    def get_sale_by_id(self, sale_id: uuid.UUID, lock: bool = False) -> Sale | None:
        stmt = select(Sale).where(Sale.id == sale_id)
        if lock:
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

    def get_sale_by_receipt(self, receipt_number: str) -> Sale | None:
        return self.db.scalar(select(Sale).where(Sale.receipt_number == receipt_number))

    def list_sales(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        cashier_id: uuid.UUID | None = None,
        status: SaleStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Sale], int]:
        stmt = select(Sale)
        if start_date:
            stmt = stmt.where(Sale.business_date >= start_date)
        if end_date:
            stmt = stmt.where(Sale.business_date <= end_date)
        if cashier_id:
            stmt = stmt.where(Sale.cashier_id == cashier_id)
        if status:
            stmt = stmt.where(Sale.status == status)

        all_matching = self.db.scalars(stmt).all()
        total = len(all_matching)

        paginated_stmt = stmt.order_by(Sale.created_at.desc()).offset(skip).limit(limit)
        items = self.db.scalars(paginated_stmt).all()
        return items, total

    def update_sale(self, sale: Sale) -> Sale:
        self.db.flush()
        return sale

    def create_refund(self, refund: SaleRefund) -> SaleRefund:
        self.db.add(refund)
        self.db.flush()
        return refund

    # ---------------- Daily / Cash / Inventory Closing Repository ----------------
    def get_or_create_daily_closing(self, business_date: date) -> DailyClosing:
        from app.modules.sales.infrastructure.models import DailyClosing, DailyClosingStatus
        closing = self.db.scalar(select(DailyClosing).where(DailyClosing.business_date == business_date))
        if not closing:
            closing = DailyClosing(
                id=uuid.uuid4(),
                business_date=business_date,
                status=DailyClosingStatus.OPEN,
            )
            self.db.add(closing)
            self.db.flush()
        return closing

    def get_daily_closing_by_date(self, business_date: date) -> DailyClosing | None:
        from app.modules.sales.infrastructure.models import DailyClosing
        return self.db.scalar(select(DailyClosing).where(DailyClosing.business_date == business_date))

    def calculate_today_cash_sales(self, business_date: date) -> float:
        stmt = select(func.coalesce(func.sum(Sale.total_amount), 0.0)).where(
            Sale.business_date == business_date,
            Sale.status.in_([SaleStatus.COMPLETED, SaleStatus.REFUNDED, SaleStatus.PARTIALLY_REFUNDED]),
        )
        return float(self.db.scalar(stmt) or 0.0)

    def calculate_today_refunds(self, business_date: date) -> float:
        stmt = select(func.coalesce(func.sum(SaleRefund.refund_amount), 0.0)).where(
            func.cast(SaleRefund.created_at, Date) == business_date
        )
        return float(self.db.scalar(stmt) or 0.0)

    def create_cash_closing(self, cash_closing: CashClosing) -> CashClosing:
        self.db.add(cash_closing)
        self.db.flush()
        return cash_closing

    def create_inventory_closing(self, inv_closing: InventoryClosing) -> InventoryClosing:
        self.db.add(inv_closing)
        self.db.flush()
        return inv_closing

    def update_daily_closing(self, closing: DailyClosing) -> DailyClosing:
        self.db.flush()
        return closing

    def list_daily_closings(self, skip: int = 0, limit: int = 50) -> tuple[Sequence[DailyClosing], int]:
        from app.modules.sales.infrastructure.models import DailyClosing
        stmt = select(DailyClosing)
        all_items = self.db.scalars(stmt).all()
        paginated_stmt = stmt.order_by(DailyClosing.business_date.desc()).offset(skip).limit(limit)
        items = self.db.scalars(paginated_stmt).all()
        return items, len(all_items)
