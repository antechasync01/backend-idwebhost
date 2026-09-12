import enum
import uuid
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class InsightCategory(str, enum.Enum):
    DEMAND = "DEMAND"
    RISK = "RISK"
    ANOMALY = "ANOMALY"
    REORDER = "REORDER"


InsightType = InsightCategory


class InsightSeverity(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


InsightPriority = InsightSeverity


class InsightStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DISMISSED = "DISMISSED"
    RESOLVED = "RESOLVED"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AIInsight(Base, TimestampMixin):
    __tablename__ = "ai_insights"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    category: Mapped[InsightCategory] = mapped_column(
        Enum(InsightCategory, name="insight_category_enum"),
        default=InsightCategory.DEMAND,
        nullable=False,
        index=True
    )
    severity: Mapped[InsightSeverity] = mapped_column(
        Enum(InsightSeverity, name="insight_severity_enum"),
        default=InsightSeverity.INFO,
        nullable=False,
        index=True
    )
    status: Mapped[InsightStatus] = mapped_column(
        Enum(InsightStatus, name="insight_status_enum"),
        default=InsightStatus.ACTIVE,
        nullable=False,
        index=True
    )
    action_recommended: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    insight_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True
    )


class StockoutRiskScore(Base, TimestampMixin):
    __tablename__ = "stockout_risk_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    daily_burn_rate: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False
    )
    current_total_stock: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    days_until_stockout: Mapped[float] = mapped_column(
        Float,
        default=999.0,
        nullable=False
    )
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="risk_level_enum"),
        default=RiskLevel.LOW,
        nullable=False,
        index=True
    )


class DemandForecast(Base, TimestampMixin):
    __tablename__ = "demand_forecasts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    forecast_date: Mapped[date] = mapped_column(
        Date,
        index=True,
        nullable=False
    )
    predicted_quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.85,
        nullable=False
    )
