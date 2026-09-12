from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.modules.products.infrastructure.models import ProductStatus, RegistrationStatus


# ---------------- Category Schemas ----------------
class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------- Product Schemas ----------------
class ProductCreate(BaseModel):
    gtin: str = Field(..., min_length=8, max_length=14, description="EAN-13 / GTIN-13 code")
    name: str = Field(..., max_length=255)
    brand: str | None = None
    category_id: uuid.UUID | None = None
    unit: str = Field("pcs", max_length=20)
    description: str | None = None
    purchase_price: float = Field(0.0, ge=0.0)
    selling_price: float = Field(0.0, ge=0.0)
    status: ProductStatus = ProductStatus.ACTIVE
    external_metadata: dict | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    brand: str | None = None
    category_id: uuid.UUID | None = None
    unit: str | None = None
    description: str | None = None
    purchase_price: float | None = Field(None, ge=0.0)
    selling_price: float | None = Field(None, ge=0.0)
    status: ProductStatus | None = None
    external_metadata: dict | None = None


class ProductResponse(BaseModel):
    id: uuid.UUID
    gtin: str
    name: str
    brand: str | None = None
    category_id: uuid.UUID | None = None
    category_name: str | None = None
    unit: str
    description: str | None = None
    purchase_price: float
    selling_price: float
    status: ProductStatus
    external_metadata: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------- Registration Request Schemas ----------------
class RegistrationRequestCreate(BaseModel):
    gtin: str = Field(..., min_length=8, max_length=14)
    suggested_name: str = Field(..., max_length=255)
    suggested_category_id: uuid.UUID | None = None
    suggested_unit: str = Field("pcs", max_length=20)
    suggested_purchase_price: float | None = Field(None, ge=0.0)
    suggested_selling_price: float | None = Field(None, ge=0.0)


class RegistrationRequestApprove(BaseModel):
    review_notes: str | None = None


class RegistrationRequestReject(BaseModel):
    review_notes: str = Field(..., min_length=1, description="Reason for rejection")


class RegistrationRequestResponse(BaseModel):
    id: uuid.UUID
    gtin: str
    suggested_name: str
    suggested_category_id: uuid.UUID | None = None
    suggested_unit: str
    suggested_purchase_price: float | None = None
    suggested_selling_price: float | None = None
    status: RegistrationStatus
    requested_by_id: uuid.UUID
    reviewed_by_id: uuid.UUID | None = None
    review_notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
