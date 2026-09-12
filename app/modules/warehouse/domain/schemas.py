from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.modules.warehouse.infrastructure.models import ReceivingStatus, WarehouseRequestStatus


# ---------------- Receiving Item Schemas ----------------
class ReceivingItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity_received: int = Field(..., gt=0, description="Quantity received must be positive")
    unit_cost: float | None = Field(None, ge=0.0)


class ReceivingItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str | None = None
    gtin: str | None = None
    quantity_received: int
    unit_cost: float | None = None

    model_config = ConfigDict(from_attributes=True)


# ---------------- Receiving Schemas ----------------
class ReceivingCreate(BaseModel):
    supplier_id: uuid.UUID | None = None
    notes: str | None = None
    items: list[ReceivingItemCreate] = Field(..., min_length=1, description="At least one receiving item is required")


class ReceivingUpdate(BaseModel):
    supplier_id: uuid.UUID | None = None
    notes: str | None = None
    items: list[ReceivingItemCreate] | None = None


class ReceivingReview(BaseModel):
    review_notes: str | None = None


class ReceivingResponse(BaseModel):
    id: uuid.UUID
    receiving_number: str
    supplier_id: uuid.UUID | None = None
    supplier_name: str | None = None
    status: ReceivingStatus
    submitted_by_id: uuid.UUID
    reviewed_by_id: uuid.UUID | None = None
    notes: str | None = None
    items: list[ReceivingItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------- Warehouse Request Schemas ----------------
class WarehouseRequestCreate(BaseModel):
    product_id: uuid.UUID
    requested_quantity: int = Field(..., gt=0)
    notes: str = Field(..., min_length=1)


class WarehouseRequestReview(BaseModel):
    notes: str | None = None


class WarehouseRequestResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str | None = None
    requested_quantity: int
    notes: str
    status: WarehouseRequestStatus
    requested_by_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
