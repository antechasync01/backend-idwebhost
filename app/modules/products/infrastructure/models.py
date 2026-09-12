import enum
import uuid
from sqlalchemy import CheckConstraint, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class ProductStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class RegistrationStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")


class Product(Base, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("purchase_price >= 0", name="ck_products_purchase_price_non_negative"),
        CheckConstraint("selling_price >= 0", name="ck_products_selling_price_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    gtin: Mapped[str] = mapped_column(
        String(14),
        unique=True,
        index=True,
        nullable=False,
        comment="EAN-13 / GTIN-13 code"
    )
    name: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False
    )
    brand: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pcs"
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    purchase_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0.00
    )
    selling_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0.00
    )
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus, name="product_status_enum"),
        nullable=False,
        default=ProductStatus.ACTIVE,
        index=True
    )
    external_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    category: Mapped["Category | None"] = relationship("Category", back_populates="products")


class ProductRegistrationRequest(Base, TimestampMixin):
    __tablename__ = "product_registration_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    gtin: Mapped[str] = mapped_column(
        String(14),
        index=True,
        nullable=False
    )
    suggested_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    suggested_category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True
    )
    suggested_unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pcs"
    )
    suggested_purchase_price: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    suggested_selling_price: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    status: Mapped[RegistrationStatus] = mapped_column(
        Enum(RegistrationStatus, name="registration_status_enum"),
        nullable=False,
        default=RegistrationStatus.PENDING,
        index=True
    )
    requested_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    reviewed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    review_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
