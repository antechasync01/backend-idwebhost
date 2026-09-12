from datetime import datetime, timezone
import uuid
from typing import Sequence
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.modules.products.infrastructure.models import Product
from app.modules.suppliers.infrastructure.models import Supplier
from app.modules.warehouse.infrastructure.models import Receiving, ReceivingItem, ReceivingStatus, WarehouseRequest, WarehouseRequestStatus


class WarehouseRepository:
    def __init__(self, db: Session):
        self.db = db

    def generate_receiving_number(self) -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        prefix = f"RCV-{date_str}-"
        
        # Count existing receivings created today for sequential numbering
        count_stmt = select(func.count(Receiving.id)).where(Receiving.receiving_number.like(f"{prefix}%"))
        count = self.db.scalar(count_stmt) or 0
        seq = count + 1
        return f"{prefix}{seq:04d}"

    def create_receiving(self, receiving: Receiving) -> Receiving:
        self.db.add(receiving)
        self.db.flush()
        return receiving

    def get_receiving_by_id(self, receiving_id: uuid.UUID, lock: bool = False) -> Receiving | None:
        stmt = select(Receiving).where(Receiving.id == receiving_id)
        if lock:
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

    def list_receivings(
        self,
        status: ReceivingStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Receiving], int]:
        stmt = select(Receiving)
        if status:
            stmt = stmt.where(Receiving.status == status)

        all_matching = self.db.scalars(stmt).all()
        total = len(all_matching)

        paginated_stmt = stmt.order_by(Receiving.created_at.desc()).offset(skip).limit(limit)
        items = self.db.scalars(paginated_stmt).all()
        return items, total

    def update_receiving(self, receiving: Receiving) -> Receiving:
        self.db.flush()
        return receiving

    # ---------------- Warehouse Requests ----------------
    def create_warehouse_request(self, req: WarehouseRequest) -> WarehouseRequest:
        self.db.add(req)
        self.db.flush()
        return req

    def get_warehouse_request_by_id(self, request_id: uuid.UUID) -> WarehouseRequest | None:
        return self.db.get(WarehouseRequest, request_id)

    def list_warehouse_requests(
        self,
        status: WarehouseRequestStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[WarehouseRequest], int]:
        stmt = select(WarehouseRequest)
        if status:
            stmt = stmt.where(WarehouseRequest.status == status)

        all_matching = self.db.scalars(stmt).all()
        total = len(all_matching)

        paginated_stmt = stmt.order_by(WarehouseRequest.created_at.desc()).offset(skip).limit(limit)
        items = self.db.scalars(paginated_stmt).all()
        return items, total

    def update_warehouse_request(self, req: WarehouseRequest) -> WarehouseRequest:
        self.db.flush()
        return req
