import uuid
from typing import Sequence
from sqlalchemy.orm import Session
from app.modules.inventory.domain.exceptions import (
    InsufficientStockError,
    InvalidAdjustmentError,
    InvalidTransferQuantityError,
    InventoryNotFoundError,
)
from app.modules.inventory.domain.schemas import (
    AdjustmentLocation,
    InventoryAdjustmentRequest,
    InventoryTransferRequest,
    TransferDirection,
)
from app.modules.inventory.infrastructure.inventory_repository import InventoryRepository
from app.modules.inventory.infrastructure.models import Inventory, InventoryMovement, MovementType
from app.modules.products.infrastructure.models import Product


class InventoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InventoryRepository(db)

    def list_inventory(
        self,
        query: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[tuple[Inventory, Product]], int]:
        return self.repo.list_inventory(query=query, skip=skip, limit=limit)

    def get_inventory_by_product_id(self, product_id: uuid.UUID) -> tuple[Inventory, Product]:
        res = self.repo.get_by_product_id(product_id)
        if not res:
            raise InventoryNotFoundError(str(product_id))
        product = self.db.get(Product, product_id)
        return res, product

    def transfer_stock(
        self,
        payload: InventoryTransferRequest,
        actor_id: uuid.UUID,
    ) -> tuple[Inventory, Product]:
        if payload.quantity <= 0:
            raise InvalidTransferQuantityError(payload.quantity)

        # Lock inventory record for update to prevent race conditions
        inventory = self.repo.get_by_product_id(payload.product_id, lock=True)
        if not inventory:
            raise InventoryNotFoundError(str(payload.product_id))

        if payload.direction == TransferDirection.ON_HAND_TO_DISPLAY:
            if inventory.on_hand_quantity < payload.quantity:
                raise InsufficientStockError(
                    available=inventory.on_hand_quantity,
                    requested=payload.quantity,
                    location="ON_HAND",
                )
            inventory.on_hand_quantity -= payload.quantity
            inventory.display_quantity += payload.quantity
            from_loc, to_loc = "ON_HAND", "DISPLAY"
        else:
            if inventory.display_quantity < payload.quantity:
                raise InsufficientStockError(
                    available=inventory.display_quantity,
                    requested=payload.quantity,
                    location="DISPLAY",
                )
            inventory.display_quantity -= payload.quantity
            inventory.on_hand_quantity += payload.quantity
            from_loc, to_loc = "DISPLAY", "ON_HAND"

        self.repo.update_inventory(inventory)

        # Create movement log
        movement = InventoryMovement(
            id=uuid.uuid4(),
            product_id=payload.product_id,
            movement_type=MovementType.DISPLAY_TRANSFER,
            quantity=payload.quantity,
            from_location=from_loc,
            to_location=to_loc,
            actor_id=actor_id,
            metadata_info={"direction": payload.direction.value},
        )
        self.repo.create_movement(movement)

        self.db.commit()
        self.db.refresh(inventory)
        product = self.db.get(Product, payload.product_id)
        return inventory, product

    def adjust_inventory(
        self,
        payload: InventoryAdjustmentRequest,
        actor_id: uuid.UUID,
    ) -> tuple[Inventory, Product]:
        if payload.quantity_change == 0:
            raise InvalidAdjustmentError("Quantity change cannot be zero.")

        # Lock inventory record for update
        inventory = self.repo.get_by_product_id(payload.product_id, lock=True)
        if not inventory:
            raise InventoryNotFoundError(str(payload.product_id))

        if payload.location == AdjustmentLocation.DISPLAY:
            new_qty = inventory.display_quantity + payload.quantity_change
            if new_qty < 0:
                raise InvalidAdjustmentError(
                    f"Resulting DISPLAY quantity cannot be negative. Current: {inventory.display_quantity}, Change: {payload.quantity_change}"
                )
            inventory.display_quantity = new_qty
            target_loc = "DISPLAY"
        else:
            new_qty = inventory.on_hand_quantity + payload.quantity_change
            if new_qty < 0:
                raise InvalidAdjustmentError(
                    f"Resulting ON_HAND quantity cannot be negative. Current: {inventory.on_hand_quantity}, Change: {payload.quantity_change}"
                )
            inventory.on_hand_quantity = new_qty
            target_loc = "ON_HAND"

        self.repo.update_inventory(inventory)

        # Create movement log
        movement = InventoryMovement(
            id=uuid.uuid4(),
            product_id=payload.product_id,
            movement_type=MovementType.ADJUSTMENT,
            quantity=payload.quantity_change,
            from_location=target_loc if payload.quantity_change < 0 else None,
            to_location=target_loc if payload.quantity_change > 0 else None,
            actor_id=actor_id,
            metadata_info={"reason": payload.reason, "location": payload.location.value},
        )
        self.repo.create_movement(movement)

        self.db.commit()
        self.db.refresh(inventory)
        product = self.db.get(Product, payload.product_id)
        return inventory, product

    def list_movements(
        self,
        product_id: uuid.UUID | None = None,
        movement_type: MovementType | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[tuple[InventoryMovement, Product]], int]:
        return self.repo.list_movements(product_id=product_id, movement_type=movement_type, skip=skip, limit=limit)
