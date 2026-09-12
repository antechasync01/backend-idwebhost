from datetime import date, datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.modules.ai.infrastructure.models import InsightCategory, InsightSeverity, RiskLevel


class AIInsightResponse(BaseModel):
    id: UUID
    title: str
    description: str
    category: InsightCategory
    severity: InsightSeverity
    action_recommended: str | None = None
    product_id: UUID | None = None
    insight_metadata: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockoutRiskResponse(BaseModel):
    id: UUID
    product_id: UUID
    product_name: str | None = None
    product_gtin: str | None = None
    product_sku: str | None = None
    daily_burn_rate: float
    current_total_stock: int
    days_until_stockout: float
    risk_level: RiskLevel
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DemandForecastResponse(BaseModel):
    id: UUID
    product_id: UUID
    product_name: str | None = None
    forecast_date: date
    predicted_quantity: float
    confidence_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HermesChatRequest(BaseModel):
    prompt: str = Field(..., description="Pesan / pertanyaan dari pengguna untuk Hermes Agent", min_length=1)
    conversation_id: str | None = Field(None, description="Session ID percakapan Hermes")


class HermesChatResponse(BaseModel):
    reply: str = Field(..., description="Jawaban reasoning dari Hermes Agent")
    conversation_id: str = Field(..., description="Session ID percakapan Hermes")
    tools_used: list[str] = Field(default_factory=list, description="Daftar MCP tools yang dipanggil selama reasoning")
    data_evidence: dict[str, Any] | None = Field(None, description="Data pendukung bukti hasil query MCP")
