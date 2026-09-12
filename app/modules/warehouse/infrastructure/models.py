import enum
import uuid
from sqlalchemy import CheckConstraint, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class ReceivingStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CORRECTION_REQUESTED = "CORRECTION_REQUESTED"


class WarehouseRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    REVIEWED = "REVIEWED"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class Receiving(Base, TimestampMixin):
    __tablename__ = "receivings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    receiving_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    status: Mapped[ReceivingStatus] = mapped_column(
        Enum(ReceivingStatus, name="receiving_status_enum"),
        default=ReceivingStatus.DRAFT,
        nullable=False,
        index=True
    )
    submitted_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True,
        nullable=False
    )
    reviewed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True,
        nullable=True
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    items: Mapped[list["ReceivingItem"]] = relationship(
        "ReceivingItem", back_populates="receiving", cascade="all, delete-orphan"
    )


class ReceivingItem(Base):
    __tablename__ = "receiving_items"
    __table_args__ = (
        CheckConstraint("quantity_received > 0", name="ck_receiving_items_qty_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    receiving_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("receivings.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        index=True,
        nullable=False
    )
    quantity_received: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    unit_cost: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    receiving: Mapped["Receiving"] = relationship("Receiving", back_populates="items")


class WarehouseRequest(Base, TimestampMixin):
    __tablename__ = "warehouse_requests"
    __table_args__ = (
        CheckConstraint("requested_quantity > 0", name="ck_warehouse_requests_qty_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        index=True,
        nullable=False
    )
    requested_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    notes: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    status: Mapped[WarehouseRequestStatus] = mapped_column(
        Enum(WarehouseRequestStatus, name="warehouse_request_status_enum"),
        default=WarehouseRequestStatus.PENDING,
        nullable=False,
        index=True
    )
    requested_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True,
        nullable=False
    )
