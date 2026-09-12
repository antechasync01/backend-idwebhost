"""Database Seeder Script for AURA POS Backend.

Seeds Roles, Permissions, RolePermissions, Users, Categories, Products, and Initial Inventory.
Run with: uv run python scripts/seed.py
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uuid
from sqlalchemy.orm import Session

from app.core.database import SessionLocal

from app.core.models import Base
from app.core.security import hash_password
from app.modules.inventory.infrastructure.models import Inventory
from app.modules.products.infrastructure.models import Category, Product, ProductStatus
from app.modules.users.infrastructure.models import Permission, Role, RolePermission, User


def seed_database():
    db: Session = SessionLocal()
    try:
        print("[START] Starting AURA POS Database Seeding...")

        # 1. Seed Roles
        role_definitions = [
            ("OWNER", "Pemilik Toko", "Akses penuh ke seluruh sistem, analytics, AI, dan persetujuan utama."),
            ("WAREHOUSE_ADMIN", "Manajer Gudang", "Kelola katalog produk, persetujuan penerimaan barang, dan penyesuaian stok."),
            ("WAREHOUSE_STAFF", "Staf Gudang", "Scan barang, pengajuan produk baru, penerimaan fisik, dan transfer display."),
            ("CASHIER", "Kasir Toko", "Transaksi penjualan POS, cetak struk, refund, dan penutupan kas harian."),
        ]

        roles: dict[str, Role] = {}
        for code, name, desc in role_definitions:
            role = db.query(Role).filter(Role.code == code).first()
            if not role:
                role = Role(id=uuid.uuid4(), code=code, name=name, description=desc)
                db.add(role)
                db.flush()
                print(f"   [+] Role created: {code}")
            roles[code] = role

        # 2. Seed Permissions
        permission_definitions = [
            ("product.read", "Melihat katalog produk", "Membaca data produk dan kategori"),
            ("product.create", "Membuat produk baru", "Menambahkan master produk baru"),
            ("product.update", "Mengubah produk", "Memperbarui detail produk"),
            ("product.approve", "Menyetujui pendaftaran produk", "Approve request pendaftaran produk baru"),
            ("inventory.read", "Melihat stok inventori", "Membaca kuantitas stok display dan on-hand"),
            ("inventory.transfer", "Transfer display", "Internal transfer stok ON_HAND <-> DISPLAY"),
            ("inventory.adjust", "Penyesuaian stok manual", "Melakukan inventory adjustment"),
            ("receiving.read", "Melihat penerimaan barang", "Membaca histori penerimaan barang gudang"),
            ("receiving.submit", "Pengajuan penerimaan", "Submit form penerimaan barang"),
            ("receiving.approve", "Persetujuan penerimaan", "Approve penerimaan barang gudang"),
            ("receiving.reject", "Penolakan penerimaan", "Reject penerimaan barang gudang"),
            ("receiving.request_correction", "Koreksi penerimaan", "Request correction penerimaan barang"),
            ("sales.create", "Transaksi kasir POS", "Membuat transaksi penjualan kasir"),
            ("sales.read", "Melihat riwayat penjualan", "Membaca transaksi penjualan"),
            ("sales.void", "Pembatalan transaksi", "Void transaksi penjualan"),
            ("sales.refund", "Pengembalian barang", "Refund transaksi penjualan"),
            ("supplier.read", "Melihat data supplier", "Membaca master supplier"),
            ("supplier.create", "Membuat supplier", "Menambahkan master supplier baru"),
            ("supplier.update", "Mengubah supplier", "Mengubah master supplier"),
            ("closing.cash", "Penutupan kas harian", "Proses cash closing kasir"),
            ("closing.inventory", "Penutupan inventori", "Proses inventory closing harian"),
            ("closing.daily", "Penutupan harian toko", "Finalisasi daily closing toko"),
            ("audit.read", "Melihat audit log", "Membaca log aktivitas sistem"),
            ("analytics.read", "Melihat analytics", "Membaca laporan bisnis dan omzet"),
            ("ai.read", "Melihat AI insight", "Membaca AI insights dan rekomendasi"),
            ("ai.investigate", "Hermes AI Reasoning", "Menggunakan conversational AI Hermes"),
        ]

        permissions: dict[str, Permission] = {}
        for code, name, desc in permission_definitions:
            perm = db.query(Permission).filter(Permission.code == code).first()
            if not perm:
                perm = Permission(id=uuid.uuid4(), code=code, name=name, description=desc)
                db.add(perm)
                db.flush()
                print(f"   [+] Permission created: {code}")
            permissions[code] = perm

        # 3. Role-Permission Matrix
        role_perm_matrix = {
            "OWNER": list(permissions.keys()),  # Full access
            "WAREHOUSE_ADMIN": [
                "product.read", "product.create", "product.update", "product.approve",
                "inventory.read", "inventory.transfer", "inventory.adjust",
                "receiving.read", "receiving.submit", "receiving.approve", "receiving.reject", "receiving.request_correction",
                "supplier.read", "closing.inventory", "audit.read", "ai.read", "ai.investigate"
            ],
            "WAREHOUSE_STAFF": [
                "product.read", "product.create", "inventory.read", "inventory.transfer",
                "receiving.read", "receiving.submit", "ai.read"
            ],
            "CASHIER": [
                "product.read", "inventory.read", "sales.create", "sales.read",
                "sales.void", "sales.refund", "closing.cash"
            ],
        }

        for role_code, perm_codes in role_perm_matrix.items():
            role_obj = roles[role_code]
            for perm_code in perm_codes:
                perm_obj = permissions[perm_code]
                rp_exists = db.query(RolePermission).filter(
                    RolePermission.role_id == role_obj.id,
                    RolePermission.permission_id == perm_obj.id
                ).first()
                if not rp_exists:
                    db.add(RolePermission(role_id=role_obj.id, permission_id=perm_obj.id))

        print("   [+] Role-Permission mappings initialized.")

        # 4. Seed Demo Users
        users_seed_data = [
            ("owner", "owner@aura.pos", "owner123", "Pemilik Toko AURA", "OWNER"),
            ("wh_admin", "admin@aura.pos", "admin123", "Admin Gudang AURA", "WAREHOUSE_ADMIN"),
            ("wh_staff", "staff@aura.pos", "staff123", "Staf Gudang AURA", "WAREHOUSE_STAFF"),
            ("cashier", "cashier@aura.pos", "cashier123", "Kasir Utama Toko", "CASHIER"),
        ]

        for username, email, password, full_name, role_code in users_seed_data:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                hashed_pw = hash_password(password)
                user = User(
                    id=uuid.uuid4(),
                    username=username,
                    email=email,
                    hashed_password=hashed_pw,
                    full_name=full_name,
                    role_id=roles[role_code].id,
                    is_active=True
                )
                db.add(user)
                print(f"   [+] User created: {username} ({role_code})")

        # 5. Seed Categories & Products
        categories_data = [
            ("Minuman", "Aneka produk minuman ringan, teh, dan air mineral"),
            ("Makanan Ringan", "Snack, biskuit, dan makanan kemasan"),
            ("Sembako", "Bahan pokok sembako: minyak, gula, beras"),
            ("Perawatan Diri", "Sabun, sampo, dan kebutuhan harian"),
        ]

        categories: dict[str, Category] = {}
        for name, desc in categories_data:
            cat = db.query(Category).filter(Category.name == name).first()
            if not cat:
                cat = Category(id=uuid.uuid4(), name=name, description=desc)
                db.add(cat)
                db.flush()
                print(f"   [+] Category created: {name}")
            categories[name] = cat

        products_data = [
            ("8996001600100", "Teh Pucuk Harum 350ml", "Mayora", "Minuman", "pcs", 3000.00, 4000.00, 30, 70),
            ("8998888110015", "Aqua Air Mineral 600ml", "Danone", "Minuman", "pcs", 2500.00, 3500.00, 40, 100),
            ("8968601111620", "Indomie Goreng Spesial 85g", "Indofood", "Makanan Ringan", "pcs", 2800.00, 3500.00, 50, 150),
            ("8992388112233", "Chitato Sapi Panggang 68g", "Indofood", "Makanan Ringan", "pcs", 8500.00, 10500.00, 20, 50),
            ("8991001100115", "Bimoli Minyak Goreng 1L", "Salim Ivomas", "Sembako", "pcs", 16000.00, 19000.00, 15, 35),
        ]

        for gtin, name, brand, cat_name, unit, purchase, selling, disp_qty, onhand_qty in products_data:
            prod = db.query(Product).filter(Product.gtin == gtin).first()
            if not prod:
                prod = Product(
                    id=uuid.uuid4(),
                    gtin=gtin,
                    name=name,
                    brand=brand,
                    category_id=categories[cat_name].id,
                    unit=unit,
                    purchase_price=purchase,
                    selling_price=selling,
                    status=ProductStatus.ACTIVE
                )
                db.add(prod)
                db.flush()
                print(f"   [+] Product created: {name} (GTIN: {gtin})")

                # Create initial inventory for product
                inv = Inventory(
                    id=uuid.uuid4(),
                    product_id=prod.id,
                    display_quantity=disp_qty,
                    on_hand_quantity=onhand_qty
                )
                db.add(inv)

        db.commit()
        print("\n[OK] AURA POS Database Seeding Completed Successfully!")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error during database seeding: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
