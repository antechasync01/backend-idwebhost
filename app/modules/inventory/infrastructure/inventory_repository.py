import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.inventory.infrastructure.models import Inventory, InventoryMovement, MovementType
from app.modules.products.infrastructure.models import Product


class InventoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_product_id(self, product_id: uuid.UUID, lock: bool = False) -> Inventory | None:
        stmt = select(Inventory).where(Inventory.product_id == product_id)
        if lock:
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

    def get_by_id(self, inventory_id: uuid.UUID, lock: bool = False) -> Inventory | None:
        stmt = select(Inventory).where(Inventory.id == inventory_id)
        if lock:
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

    def list_inventory(
        self,
        query: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[tuple[Inventory, Product]], int]:
        stmt = select(Inventory, Product).join(Product, Inventory.product_id == Product.id)
        if query:
            pattern = f"%{query}%"
            stmt = stmt.where((Product.name.ilike(pattern)) | (Product.gtin.ilike(pattern)))
        
        all_results = self.db.execute(stmt).all()
        total = len(all_results)
        
        paginated_stmt = stmt.order_by(Product.name).offset(skip).limit(limit)
        results = self.db.execute(paginated_stmt).all()
        return [(row.Inventory, row.Product) for row in results], total

    def update_inventory(self, inventory: Inventory) -> Inventory:
        self.db.flush()
        return inventory

    def create_movement(self, movement: InventoryMovement) -> InventoryMovement:
        self.db.add(movement)
        self.db.flush()
        return movement

    def list_movements(
        self,
        product_id: uuid.UUID | None = None,
        movement_type: MovementType | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[tuple[InventoryMovement, Product]], int]:
        stmt = select(InventoryMovement, Product).join(Product, InventoryMovement.product_id == Product.id)
        if product_id:
            stmt = stmt.where(InventoryMovement.product_id == product_id)
        if movement_type:
            stmt = stmt.where(InventoryMovement.movement_type == movement_type)

        all_results = self.db.execute(stmt).all()
        total = len(all_results)

        paginated_stmt = stmt.order_by(InventoryMovement.occurred_at.desc()).offset(skip).limit(limit)
        results = self.db.execute(paginated_stmt).all()
        return [(row.InventoryMovement, row.Product) for row in results], total
