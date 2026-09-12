from datetime import date, datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.modules.sales.infrastructure.models import PaymentMethod, SaleStatus


# ---------------- Sale Item Schemas ----------------
class SaleItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0, description="Item quantity must be positive")
    unit_price: float | None = Field(None, ge=0.0, description="Optional custom unit price, defaults to master selling price")


class SaleItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str | None = None
    gtin: str | None = None
    quantity: int
    unit_price: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)


# ---------------- Sale Schemas ----------------
class SaleCreateRequest(BaseModel):
    items: list[SaleItemCreate] = Field(..., min_length=1, description="Cart items required for checkout")
    cash_paid: float = Field(..., ge=0.0, description="Total cash given by customer")
    payment_method: PaymentMethod = PaymentMethod.CASH
    idempotency_key: str | None = Field(None, max_length=100)


class SaleResponse(BaseModel):
    id: uuid.UUID
    receipt_number: str
    business_date: date
    cashier_id: uuid.UUID
    total_amount: float
    payment_method: PaymentMethod
    cash_paid: float
    cash_change: float
    status: SaleStatus
    idempotency_key: str | None = None
    items: list[SaleItemResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------- Sale Refund Schemas ----------------
class SaleRefundItemCreate(BaseModel):
    sale_item_id: uuid.UUID
    quantity: int = Field(..., gt=0)


class SaleRefundItemResponse(BaseModel):
    id: uuid.UUID
    sale_item_id: uuid.UUID
    product_name: str | None = None
    quantity: int
    refund_amount: float

    model_config = ConfigDict(from_attributes=True)


class SaleRefundRequest(BaseModel):
    reason: str | None = Field(None, description="Reason for refund")
    items: list[SaleRefundItemCreate] = Field(..., min_length=1)


class SaleRefundResponse(BaseModel):
    id: uuid.UUID
    sale_id: uuid.UUID
    refund_number: str
    refund_amount: float
    reason: str | None = None
    processed_by_id: uuid.UUID
    items: list[SaleRefundItemResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------- Closing Schemas ----------------
class CashClosingSummaryResponse(BaseModel):
    business_date: date
    opening_cash: float
    cash_sales: float
    refunds: float
    cash_adjustment: float
    expected_cash: float


class CashClosingRequest(BaseModel):
    opening_cash: float = Field(0.0, ge=0.0, description="Opening cash drawer amount")
    actual_cash: float = Field(..., ge=0.0, description="Physical cash counted in drawer at closing")
    cash_adjustment: float = Field(0.0, description="Manual cash adjustment (+ or -)")
    adjustment_notes: str | None = None
    notes: str | None = None


class CashClosingResponse(BaseModel):
    id: uuid.UUID
    daily_closing_id: uuid.UUID
    cashier_id: uuid.UUID
    opening_cash: float
    cash_sales: float
    refunds: float
    cash_adjustment: float
    adjustment_notes: str | None = None
    expected_cash: float
    actual_cash: float
    variance: float
    notes: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventoryClosingItemCreate(BaseModel):
    product_id: uuid.UUID
    physical_display_quantity: int = Field(..., ge=0)
    physical_on_hand_quantity: int = Field(..., ge=0)


class InventoryClosingItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str | None = None
    opening_display_quantity: int
    opening_on_hand_quantity: int
    receiving_quantity: int
    sales_quantity: int
    adjustment_quantity: int
    return_quantity: int
    expected_display_quantity: int
    expected_on_hand_quantity: int
    physical_display_quantity: int
    physical_on_hand_quantity: int
    display_variance: int
    on_hand_variance: int
    status: str

    model_config = ConfigDict(from_attributes=True)


class InventoryClosingRequest(BaseModel):
    notes: str | None = None
    items: list[InventoryClosingItemCreate] = Field(..., min_length=1)


class InventoryClosingResponse(BaseModel):
    id: uuid.UUID
    daily_closing_id: uuid.UUID
    status: str
    notes: str | None = None
    items: list[InventoryClosingItemResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailyClosingResponse(BaseModel):
    id: uuid.UUID
    business_date: date
    status: str
    closed_by_id: uuid.UUID | None = None
    cash_closing: CashClosingResponse | None = None
    inventory_closing: InventoryClosingResponse | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
