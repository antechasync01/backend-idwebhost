import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SalesSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    gross_revenue: float = Field(..., description="Total revenue from completed sales before refunds")
    total_refunds: float = Field(..., description="Total value of processed refunds")
    net_revenue: float = Field(..., description="Gross revenue minus total refunds")
    transaction_count: int = Field(..., description="Total completed sale transactions")
    average_transaction_value: float = Field(..., description="Average basket value per sale")
    total_items_sold: int = Field(..., description="Total quantity of individual items sold")
    start_date: datetime
    end_date: datetime


class TopProductItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: uuid.UUID
    gtin: str
    product_name: str
    quantity_sold: int
    total_revenue: float


class TopProductsResponse(BaseModel):
    items: list[TopProductItem]
    start_date: datetime
    end_date: datetime


class InventoryHealthResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_products: int
    total_display_quantity: int
    total_on_hand_quantity: int
    total_inventory_quantity: int
    total_inventory_cost_value: float
    total_inventory_retail_value: float
    low_stock_product_count: int
    out_of_stock_product_count: int


class DailySalesTrendItem(BaseModel):
    date: str  # Format: YYYY-MM-DD
    gross_revenue: float
    refunds: float
    net_revenue: float
    transaction_count: int


class SalesTrendResponse(BaseModel):
    items: list[DailySalesTrendItem]
    start_date: datetime
    end_date: datetime
