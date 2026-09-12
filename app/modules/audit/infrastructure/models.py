import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Enum, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ActorType(str, enum.Enum):
    OWNER = "OWNER"
    WAREHOUSE_ADMIN = "WAREHOUSE_ADMIN"
    WAREHOUSE_STAFF = "WAREHOUSE_STAFF"
    CASHIER = "CASHIER"
    AI = "AI"
    SYSTEM = "SYSTEM"


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        index=True,
        nullable=True
    )
    actor_type: Mapped[ActorType] = mapped_column(
        Enum(ActorType, name="actor_type_enum"),
        nullable=False,
        index=True
    )
    action: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False
    )
    entity_type: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False
    )
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    before_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )
    after_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )
    metadata_info: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False
    )
