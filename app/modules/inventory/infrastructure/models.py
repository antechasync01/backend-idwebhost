import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class MovementType(str, enum.Enum):
    PURCHASE_RECEIVING = "PURCHASE_RECEIVING"
    SALE = "SALE"
    RETURN = "RETURN"
    ADJUSTMENT = "ADJUSTMENT"
    DAMAGE = "DAMAGE"
    EXPIRY = "EXPIRY"
    DISPLAY_TRANSFER = "DISPLAY_TRANSFER"
    STOCK_OPNAME = "STOCK_OPNAME"


class StockOpnameStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    CANCELLED = "CANCELLED"


class StockOpnameItemStatus(str, enum.Enum):
    MATCHED = "MATCHED"
    VARIANCE_DETECTED = "VARIANCE_DETECTED"
    ADJUSTED = "ADJUSTED"


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint("display_quantity >= 0", name="ck_inventory_display_qty_non_negative"),
        CheckConstraint("on_hand_quantity >= 0", name="ck_inventory_on_hand_qty_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )
    display_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    on_hand_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    @property
    def total_available(self) -> int:
        """Derived property: total available stock = display + on_hand."""
        return self.display_quantity + self.on_hand_quantity


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    __table_args__ = (
        Index("ix_inventory_movements_prod_type", "product_id", "movement_type"),
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
    movement_type: Mapped[MovementType] = mapped_column(
        Enum(MovementType, name="movement_type_enum"),
        nullable=False,
        index=True
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    from_location: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )
    to_location: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )
    reference_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    reference_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True,
        nullable=True
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False
    )
    metadata_info: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )


class StockOpname(Base, TimestampMixin):
    __tablename__ = "stock_opnames"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    opname_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    status: Mapped[StockOpnameStatus] = mapped_column(
        Enum(StockOpnameStatus, name="stock_opname_status_enum"),
        default=StockOpnameStatus.DRAFT,
        nullable=False,
        index=True
    )
    started_by_id: Mapped[uuid.UUID] = mapped_column(
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

    items: Mapped[list["StockOpnameItem"]] = relationship(
        "StockOpnameItem", back_populates="stock_opname", cascade="all, delete-orphan"
    )


class StockOpnameItem(Base, TimestampMixin):
    __tablename__ = "stock_opname_items"
    __table_args__ = (
        UniqueConstraint("stock_opname_id", "product_id", name="uq_stock_opname_items_opname_product"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    stock_opname_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stock_opnames.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        index=True,
        nullable=False
    )
    system_display_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    system_on_hand_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    physical_display_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    physical_on_hand_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    display_variance: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    on_hand_variance: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    status: Mapped[StockOpnameItemStatus] = mapped_column(
        Enum(StockOpnameItemStatus, name="stock_opname_item_status_enum"),
        default=StockOpnameItemStatus.MATCHED,
        nullable=False
    )

    stock_opname: Mapped["StockOpname"] = relationship("StockOpname", back_populates="items")
