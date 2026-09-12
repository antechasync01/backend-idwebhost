import enum
import uuid
from datetime import date, datetime, timezone
from sqlalchemy import CheckConstraint, Date, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class SaleStatus(str, enum.Enum):
    COMPLETED = "COMPLETED"
    VOIDED = "VOIDED"
    REFUNDED = "REFUNDED"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"


class PaymentMethod(str, enum.Enum):
    CASH = "CASH"


class DailyClosingStatus(str, enum.Enum):
    OPEN = "OPEN"
    CASH_CLOSED = "CASH_CLOSED"
    INVENTORY_CLOSED = "INVENTORY_CLOSED"
    FINALIZED = "FINALIZED"


class InventoryClosingVarianceStatus(str, enum.Enum):
    MATCHED = "MATCHED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    ADJUSTED = "ADJUSTED"
    RESOLVED = "RESOLVED"


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="ck_sales_total_amount_non_negative"),
        CheckConstraint("cash_paid >= 0", name="ck_sales_cash_paid_non_negative"),
        Index("ix_sales_date_cashier", "business_date", "cashier_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    receipt_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    business_date: Mapped[date] = mapped_column(
        Date,
        index=True,
        nullable=False
    )
    cashier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True,
        nullable=False
    )
    total_amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="payment_method_enum"),
        default=PaymentMethod.CASH,
        nullable=False
    )
    cash_paid: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    cash_change: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    status: Mapped[SaleStatus] = mapped_column(
        Enum(SaleStatus, name="sale_status_enum"),
        default=SaleStatus.COMPLETED,
        nullable=False,
        index=True
    )
    idempotency_key: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    items: Mapped[list["SaleItem"]] = relationship(
        "SaleItem", back_populates="sale", cascade="all, delete-orphan"
    )
    refunds: Mapped[list["SaleRefund"]] = relationship(
        "SaleRefund", back_populates="sale", cascade="all, delete-orphan"
    )


class SaleItem(Base):
    __tablename__ = "sale_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_sale_items_qty_positive"),
        CheckConstraint("unit_price >= 0", name="ck_sale_items_unit_price_non_negative"),
        CheckConstraint("subtotal >= 0", name="ck_sale_items_subtotal_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    sale_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        index=True,
        nullable=False
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    unit_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    subtotal: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    sale: Mapped["Sale"] = relationship("Sale", back_populates="items")


class SaleRefund(Base):
    __tablename__ = "sale_refunds"
    __table_args__ = (
        CheckConstraint("refund_amount >= 0", name="ck_sale_refunds_amount_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    sale_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    refund_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    refund_amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    processed_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    sale: Mapped["Sale"] = relationship("Sale", back_populates="refunds")
    items: Mapped[list["SaleRefundItem"]] = relationship(
        "SaleRefundItem", back_populates="refund", cascade="all, delete-orphan"
    )


class SaleRefundItem(Base):
    __tablename__ = "sale_refund_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_sale_refund_items_qty_positive"),
        CheckConstraint("refund_amount >= 0", name="ck_sale_refund_items_amount_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    refund_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sale_refunds.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    sale_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sale_items.id"),
        index=True,
        nullable=False
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    refund_amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    refund: Mapped["SaleRefund"] = relationship("SaleRefund", back_populates="items")


class DailyClosing(Base, TimestampMixin):
    __tablename__ = "daily_closings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    business_date: Mapped[date] = mapped_column(
        Date,
        unique=True,
        index=True,
        nullable=False
    )
    status: Mapped[DailyClosingStatus] = mapped_column(
        Enum(DailyClosingStatus, name="daily_closing_status_enum"),
        default=DailyClosingStatus.OPEN,
        nullable=False,
        index=True
    )
    closed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )

    cash_closing: Mapped["CashClosing | None"] = relationship("CashClosing", back_populates="daily_closing", uselist=False)
    inventory_closing: Mapped["InventoryClosing | None"] = relationship("InventoryClosing", back_populates="daily_closing", uselist=False)


class CashClosing(Base):
    __tablename__ = "cash_closings"
    __table_args__ = (
        CheckConstraint("opening_cash >= 0", name="ck_cash_closings_opening_cash_non_negative"),
        CheckConstraint("cash_sales >= 0", name="ck_cash_closings_cash_sales_non_negative"),
        CheckConstraint("refunds >= 0", name="ck_cash_closings_refunds_non_negative"),
        CheckConstraint("actual_cash >= 0", name="ck_cash_closings_actual_cash_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    daily_closing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("daily_closings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    cashier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True,
        nullable=False
    )
    opening_cash: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    cash_sales: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    refunds: Mapped[float] = mapped_column(
        Numeric(12, 2),
        default=0.00,
        nullable=False
    )
    cash_adjustment: Mapped[float] = mapped_column(
        Numeric(12, 2),
        default=0.00,
        nullable=False
    )
    adjustment_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    expected_cash: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    actual_cash: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    variance: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    daily_closing: Mapped["DailyClosing"] = relationship("DailyClosing", back_populates="cash_closing")


class InventoryClosing(Base, TimestampMixin):
    __tablename__ = "inventory_closings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    daily_closing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("daily_closings.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )
    status: Mapped[InventoryClosingVarianceStatus] = mapped_column(
        Enum(InventoryClosingVarianceStatus, name="inventory_closing_variance_status_enum"),
        default=InventoryClosingVarianceStatus.MATCHED,
        nullable=False
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    daily_closing: Mapped["DailyClosing"] = relationship("DailyClosing", back_populates="inventory_closing")
    items: Mapped[list["InventoryClosingItem"]] = relationship(
        "InventoryClosingItem", back_populates="inventory_closing", cascade="all, delete-orphan"
    )


class InventoryClosingItem(Base, TimestampMixin):
    __tablename__ = "inventory_closing_items"
    __table_args__ = (
        UniqueConstraint("inventory_closing_id", "product_id", name="uq_inventory_closing_items_closing_product"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    inventory_closing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inventory_closings.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        index=True,
        nullable=False
    )
    opening_display_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    opening_on_hand_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    receiving_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    sales_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    adjustment_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    return_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    other_movement_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    expected_display_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    expected_on_hand_quantity: Mapped[int] = mapped_column(
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
    status: Mapped[InventoryClosingVarianceStatus] = mapped_column(
        Enum(InventoryClosingVarianceStatus, name="inventory_closing_variance_status_enum"),
        default=InventoryClosingVarianceStatus.MATCHED,
        nullable=False
    )

    inventory_closing: Mapped["InventoryClosing"] = relationship("InventoryClosing", back_populates="items")
