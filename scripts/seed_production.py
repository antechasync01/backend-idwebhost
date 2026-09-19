"""Production Seed Script for AURA POS Backend.

Seeds only essential data for production:
- Roles (OWNER, WAREHOUSE_ADMIN, WAREHOUSE_STAFF, CASHIER)
- Permissions (all system permissions)
- Role-Permission mappings
- Initial users (configurable via environment variables or defaults)

Run with: uv run python scripts/seed_production.py

Environment variables (optional):
  OWNER_USERNAME    - Owner username       (default: owner)
  OWNER_EMAIL       - Owner email          (default: owner@aura.pos)
  OWNER_PASSWORD    - Owner password       (default: ChangeMe!2026)
  OWNER_FULLNAME    - Owner full name      (default: Pemilik Toko)
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uuid
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.core.models import Base
from app.core.security import hash_password
from app.modules.users.infrastructure.models import Permission, Role, RolePermission, User


# ──────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────

ROLE_DEFINITIONS = [
    ("OWNER", "Pemilik Toko", "Akses penuh ke seluruh sistem, analytics, AI, dan persetujuan utama."),
    ("WAREHOUSE_ADMIN", "Manajer Gudang", "Kelola katalog produk, persetujuan penerimaan barang, dan penyesuaian stok."),
    ("WAREHOUSE_STAFF", "Staf Gudang", "Scan barang, pengajuan produk baru, penerimaan fisik, dan transfer display."),
    ("CASHIER", "Kasir Toko", "Transaksi penjualan POS, cetak struk, refund, dan penutupan kas harian."),
]

PERMISSION_DEFINITIONS = [
    # Product
    ("product.read", "Melihat katalog produk", "Membaca data produk dan kategori"),
    ("product.create", "Membuat produk baru", "Menambahkan master produk baru"),
    ("product.update", "Mengubah produk", "Memperbarui detail produk"),
    ("product.approve", "Menyetujui pendaftaran produk", "Approve request pendaftaran produk baru"),
    # Inventory
    ("inventory.read", "Melihat stok inventori", "Membaca kuantitas stok display dan on-hand"),
    ("inventory.transfer", "Transfer display", "Internal transfer stok ON_HAND <-> DISPLAY"),
    ("inventory.adjust", "Penyesuaian stok manual", "Melakukan inventory adjustment"),
    # Receiving
    ("receiving.read", "Melihat penerimaan barang", "Membaca histori penerimaan barang gudang"),
    ("receiving.submit", "Pengajuan penerimaan", "Submit form penerimaan barang"),
    ("receiving.approve", "Persetujuan penerimaan", "Approve penerimaan barang gudang"),
    ("receiving.reject", "Penolakan penerimaan", "Reject penerimaan barang gudang"),
    ("receiving.request_correction", "Koreksi penerimaan", "Request correction penerimaan barang"),
    # Sales
    ("sales.create", "Transaksi kasir POS", "Membuat transaksi penjualan kasir"),
    ("sales.read", "Melihat riwayat penjualan", "Membaca transaksi penjualan"),
    ("sales.void", "Pembatalan transaksi", "Void transaksi penjualan"),
    ("sales.refund", "Pengembalian barang", "Refund transaksi penjualan"),
    # Supplier
    ("supplier.read", "Melihat data supplier", "Membaca master supplier"),
    ("supplier.create", "Membuat supplier", "Menambahkan master supplier baru"),
    ("supplier.update", "Mengubah supplier", "Mengubah master supplier"),
    # Closing
    ("closing.cash", "Penutupan kas harian", "Proses cash closing kasir"),
    ("closing.inventory", "Penutupan inventori", "Proses inventory closing harian"),
    ("closing.daily", "Penutupan harian toko", "Finalisasi daily closing toko"),
    # System
    ("audit.read", "Melihat audit log", "Membaca log aktivitas sistem"),
    ("analytics.read", "Melihat analytics", "Membaca laporan bisnis dan omzet"),
    ("ai.read", "Melihat AI insight", "Membaca AI insights dan rekomendasi"),
    ("ai.investigate", "Hermes AI Reasoning", "Menggunakan conversational AI Hermes"),
]

ROLE_PERMISSION_MATRIX = {
    "OWNER": "__ALL__",  # Special: gets every permission
    "WAREHOUSE_ADMIN": [
        "product.read", "product.create", "product.update", "product.approve",
        "inventory.read", "inventory.transfer", "inventory.adjust",
        "receiving.read", "receiving.submit", "receiving.approve", "receiving.reject", "receiving.request_correction",
        "supplier.read", "closing.inventory", "audit.read", "ai.read", "ai.investigate",
    ],
    "WAREHOUSE_STAFF": [
        "product.read", "product.create", "inventory.read", "inventory.transfer",
        "receiving.read", "receiving.submit", "ai.read",
    ],
    "CASHIER": [
        "product.read", "inventory.read", "sales.create", "sales.read",
        "sales.void", "sales.refund", "closing.cash",
    ],
}

# Default production users — override via env vars for security
PRODUCTION_USERS = [
    {
        "username": os.environ.get("OWNER_USERNAME", "owner"),
        "email": os.environ.get("OWNER_EMAIL", "owner@aura.pos"),
        "password": os.environ.get("OWNER_PASSWORD", "ChangeMe!2026"),
        "full_name": os.environ.get("OWNER_FULLNAME", "Pemilik Toko"),
        "role_code": "OWNER",
    },
]


# ──────────────────────────────────────────────────────────────
# Seed Functions
# ──────────────────────────────────────────────────────────────

def seed_roles(db: Session) -> dict[str, Role]:
    """Create or fetch all roles. Returns {code: Role} mapping."""
    roles: dict[str, Role] = {}
    for code, name, desc in ROLE_DEFINITIONS:
        role = db.query(Role).filter(Role.code == code).first()
        if not role:
            role = Role(id=uuid.uuid4(), code=code, name=name, description=desc)
            db.add(role)
            db.flush()
            print(f"  [+] Role created: {code}")
        else:
            print(f"  [=] Role exists: {code}")
        roles[code] = role
    return roles


def seed_permissions(db: Session) -> dict[str, Permission]:
    """Create or fetch all permissions. Returns {code: Permission} mapping."""
    permissions: dict[str, Permission] = {}
    created_count = 0
    for code, name, desc in PERMISSION_DEFINITIONS:
        perm = db.query(Permission).filter(Permission.code == code).first()
        if not perm:
            perm = Permission(id=uuid.uuid4(), code=code, name=name, description=desc)
            db.add(perm)
            db.flush()
            created_count += 1
        permissions[code] = perm
    print(f"  [+] Permissions: {created_count} created, {len(permissions) - created_count} already existed")
    return permissions


def seed_role_permissions(
    db: Session,
    roles: dict[str, Role],
    permissions: dict[str, Permission],
) -> None:
    """Map permissions to roles based on the matrix."""
    assigned_count = 0
    for role_code, perm_codes in ROLE_PERMISSION_MATRIX.items():
        role_obj = roles[role_code]

        # Resolve "__ALL__" to all permission codes
        if perm_codes == "__ALL__":
            perm_codes = list(permissions.keys())

        for perm_code in perm_codes:
            perm_obj = permissions[perm_code]
            exists = db.query(RolePermission).filter(
                RolePermission.role_id == role_obj.id,
                RolePermission.permission_id == perm_obj.id,
            ).first()
            if not exists:
                db.add(RolePermission(role_id=role_obj.id, permission_id=perm_obj.id))
                assigned_count += 1

    print(f"  [+] Role-Permission mappings: {assigned_count} new assignments")


def seed_users(db: Session, roles: dict[str, Role]) -> None:
    """Create production users (idempotent)."""
    for user_data in PRODUCTION_USERS:
        username = user_data["username"]
        user = db.query(User).filter(User.username == username).first()
        if not user:
            hashed_pw = hash_password(user_data["password"])
            user = User(
                id=uuid.uuid4(),
                username=username,
                email=user_data["email"],
                hashed_password=hashed_pw,
                full_name=user_data["full_name"],
                role_id=roles[user_data["role_code"]].id,
                is_active=True,
            )
            db.add(user)
            print(f"  [+] User created: {username} ({user_data['role_code']})")
        else:
            print(f"  [=] User exists: {username}")


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def seed_production():
    print("=" * 55)
    print("  AURA POS — Production Database Seed")
    print("=" * 55)

    print("\n[*] Verifying database tables exist...")
    Base.metadata.create_all(bind=engine)
    print("    [OK] Tables verified / created.")

    db: Session = SessionLocal()
    try:

        print("\n[1/4] Seeding Roles...")
        roles = seed_roles(db)

        print("\n[2/4] Seeding Permissions...")
        permissions = seed_permissions(db)

        print("\n[3/4] Seeding Role-Permission Mappings...")
        seed_role_permissions(db, roles, permissions)

        print("\n[4/4] Seeding Production Users...")
        seed_users(db, roles)

        db.commit()

        print("\n" + "=" * 55)
        print("  [OK] Production seed completed successfully!")
        print("=" * 55)
        print("\n[!] Reminder: Change the default owner password after first login!")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error during production seed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_production()
