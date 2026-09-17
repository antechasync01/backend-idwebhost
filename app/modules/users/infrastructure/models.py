import enum
import uuid
from datetime import datetime, date as dt_date
from sqlalchemy import Boolean, Enum, ForeignKey, String, Text, UniqueConstraint, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin


class UserRole(str, enum.Enum):
    OWNER = "OWNER"
    WAREHOUSE_ADMIN = "WAREHOUSE_ADMIN"
    WAREHOUSE_STAFF = "WAREHOUSE_STAFF"
    CASHIER = "CASHIER"


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )
    users: Mapped[list["User"]] = relationship("User", back_populates="role_rel")


class Permission(Base, TimestampMixin):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    roles: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="permission", cascade="all, delete-orphan"
    )


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permissions_role_permission"),
    )

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True
    )

    role: Mapped["Role"] = relationship("Role", back_populates="permissions")
    permission: Mapped["Permission"] = relationship("Permission", back_populates="roles")


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    role_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id"),
        nullable=True,
        index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    role_rel: Mapped["Role | None"] = relationship("Role", back_populates="users")

    @property
    def role(self) -> UserRole | None:
        """Returns role code enum (e.g. UserRole.OWNER) or None."""
        if self.role_rel and self.role_rel.code:
            try:
                return UserRole(self.role_rel.code)
            except ValueError:
                return None
        return None

    @role.setter
    def role(self, value: UserRole | str | None) -> None:
        """Sets the role property by attaching a Role object to role_rel."""
        if value is None:
            self.role_rel = None
        else:
            code_str = value.value if isinstance(value, enum.Enum) else value
            self.role_rel = Role(code=code_str)


class Attendance(Base, TimestampMixin):
    __tablename__ = "attendances"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    clock_in_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    clock_out_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    date: Mapped[dt_date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    user: Mapped["User"] = relationship("User", backref="attendances")
