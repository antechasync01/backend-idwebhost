import uuid
from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class Supplier(Base, TimestampMixin):
    __tablename__ = "suppliers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False
    )
    contact_person: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    whatsapp: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    supplier_products: Mapped[list["SupplierProduct"]] = relationship(
        "SupplierProduct", back_populates="supplier", cascade="all, delete-orphan"
    )


class SupplierProduct(Base):
    __tablename__ = "supplier_products"
    __table_args__ = (
        UniqueConstraint("supplier_id", "product_id", name="uq_supplier_product"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    supplier_product_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    purchase_price: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="supplier_products")
