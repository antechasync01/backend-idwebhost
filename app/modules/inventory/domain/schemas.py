from datetime import datetime
import enum
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.modules.inventory.infrastructure.models import MovementType


class TransferDirection(str, enum.Enum):
    ON_HAND_TO_DISPLAY = "ON_HAND_TO_DISPLAY"
    DISPLAY_TO_ON_HAND = "DISPLAY_TO_ON_HAND"


class AdjustmentLocation(str, enum.Enum):
    DISPLAY = "DISPLAY"
    ON_HAND = "ON_HAND"


# ---------------- Inventory Schemas ----------------
class InventoryResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str | None = None
    gtin: str | None = None
    display_quantity: int
    on_hand_quantity: int
    total_available: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventoryTransferRequest(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0, description="Quantity to transfer")
    direction: TransferDirection = Field(..., description="ON_HAND_TO_DISPLAY or DISPLAY_TO_ON_HAND")


class InventoryAdjustmentRequest(BaseModel):
    product_id: uuid.UUID
    location: AdjustmentLocation = Field(..., description="DISPLAY or ON_HAND")
    quantity_change: int = Field(..., description="Positive to add, negative to reduce")
    reason: str = Field(..., min_length=1, description="Reason for adjustment (e.g. Damage, Expiry, Manual Count)")


# ---------------- Movement Schemas ----------------
class InventoryMovementResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str | None = None
    movement_type: MovementType
    quantity: int
    from_location: str | None = None
    to_location: str | None = None
    reference_type: str | None = None
    reference_id: uuid.UUID | None = None
    actor_id: uuid.UUID | None = None
    occurred_at: datetime
    metadata_info: dict | None = None

    model_config = ConfigDict(from_attributes=True)
