AURA Database — Improvement Checklist
Prioritas Area Kondisi Sekarang Perbaikan
🔴 P0 users.role Ada role + role_id Hapus role, gunakan role_id
🔴 P0 Daily Closing business_date belum terlihat unique UNIQUE(business_date)
🔴 P0 Inventory Closing 1 closing belum dibatasi UNIQUE(daily_closing_id)
🔴 P0 Inventory Closing Items Sudah ada UNIQUE(inventory_closing_id, product_id)
🔴 P0 Stock Opname Items Sudah ada UNIQUE(stock_opname_id, product_id)
🔴 P0 Supplier Products Junction table sudah benar UNIQUE(supplier_id, product_id)
🔴 P0 Inventory Source of truth belum cukup dikunci Constraint + transaction rules
🔴 P0 Money fields Perlu konsistensi tipe Gunakan NUMERIC, bukan float
🔴 P0 Quantity fields Perlu konsistensi Tentukan precision/scale
🟠 P1 Sales Refund semantics belum jelas Tentukan lifecycle/refund model
🟠 P1 Cash Closing Adjustment sudah ada Tambahkan constraint/formula validation
🟠 P1 RBAC Sudah bagus Tambahkan unique constraints
🟠 P1 Inventory Movement Generic reference Tetapkan enum + business rules
🟠 P1 Product GTIN perlu unique UNIQUE(gtin) bila applicable
🟠 P1 Receipt / Receiving Number Perlu uniqueness Unique per business domain
🟠 P1 Audit Log Sudah bagus Append-only + index
🟠 P1 Notifications Generic reference Tambahkan index
🟡 P2 Events Masih minimal Validasi kebutuhan Event Intelligence
🟡 P2 AI Insights Sudah cukup baik Pastikan evidence JSONB + status
🟡 P2 Indexing Belum terlihat Tambahkan index FK/query-heavy
🟡 P2 Delete policy Belum terlihat Hindari hard delete historical data

Sekarang saya breakdown satu per satu.

🔴 P0 — Wajib diperbaiki

1. users: hapus role

Sekarang Anda punya kira-kira:

users
├── role
└── role_id

Ini redundant.

Ubah menjadi:
users
├── id
├── username
├── email
├── hashed_password
├── full_name
├── is_active
├── role_id FK
├── created_at
└── updated_at

Relationship:

users
│
│ N:1
▼
roles

Jangan menyimpan role dua kali.

2. daily_closings.business_date → UNIQUE

Karena AURA single-store:

2026-09-06 → hanya boleh ada 1 daily closing

Tambahkan:

UNIQUE (business_date)

Jadi:

## daily_closings

id
business_date UNIQUE
status
closed_by_id
created_at
updated_at 3. inventory_closings.daily_closing_id → UNIQUE

Struktur yang kita inginkan:

daily_closings
│
│ 1:1
▼
inventory_closings
│
│ 1:N
▼
inventory_closing_items

Maka:

UNIQUE (daily_closing_id) 4. inventory_closing_items

Strukturnya sekarang sudah bagus.

Tambahkan:

UNIQUE (
inventory_closing_id,
product_id
)

Artinya satu produk hanya boleh muncul sekali dalam satu inventory closing.

5. stock_opname_items

Sama:

UNIQUE (
stock_opname_id,
product_id
)

Karena:

Stock Opname #001
├── Product A
├── Product B
├── Product C

tidak boleh:

Stock Opname #001
├── Product A
├── Product A ← ❌ 6. supplier_products

Tambahkan:

UNIQUE (
supplier_id,
product_id
)

Sehingga satu supplier-product pair tidak duplicate.

Kemudian is_primary perlu business rule:

satu product hanya memiliki satu primary supplier.

Untuk PostgreSQL, ini idealnya menggunakan partial unique index.

7. Inventory harus benar-benar menjadi source of truth

Ini area paling penting secara backend.

Anda memiliki:

inventory

- product_id
- display_quantity
- on_hand_quantity

dan:

inventory_movements

- product_id
- quantity
- movement_type

Yang harus kita tetapkan:

Jangan lakukan
UPDATE inventory

sendirian.

Semua mutation harus:
BEGIN TRANSACTION

SELECT inventory
FOR UPDATE

UPDATE inventory

INSERT inventory_movements

INSERT audit_logs

COMMIT

Contoh sale:

Sale
│
├── sale
├── sale_items
│
├── lock inventory
│
├── decrement inventory
│
├── inventory_movement
│
└── audit_log

Ini bukan sekadar masalah schema, tapi harus menjadi invariant backend.

8. Semua uang gunakan NUMERIC

Untuk:

purchase_price
selling_price
unit_price
subtotal
total_amount
cash_paid
cash_change
opening_cash
cash_sales
refunds
expected_cash
actual_cash
variance
cash_adjustment

gunakan:

NUMERIC(18,2)

Jangan gunakan FLOAT.

Contoh:

Numeric(18, 2)

Ini penting untuk POS.

9. Quantity harus punya tipe yang konsisten

Sekarang banyak quantity menggunakan angka.

Kita harus menentukan apakah AURA hanya mendukung:

1 pcs
2 pcs
10 pcs

atau juga:

1.5 kg
0.25 liter

Kalau produk AURA bisa memiliki decimal quantity, gunakan misalnya:

NUMERIC(18,3)

untuk quantity.

Kalau semuanya integer, gunakan:

INTEGER

Ini perlu diputuskan secara eksplisit sebelum schema final.

🟠 P1 — Sangat disarankan 10. Sales + Refund perlu diperjelas

Saat ini:

sales
├── status
├── total_amount
├── cash_paid
└── cash_change

Sedangkan cash closing memiliki:

refunds

Kita perlu menentukan apakah refund adalah:

Option A

Refund hanya mengubah status sale.

atau:

Option B — lebih proper
sales
│
▼
sale_refunds
│
▼
sale_refund_items

Kalau AURA memang akan melakukan refund sebagai operational transaction, Option B lebih aman karena refund merupakan transaksi tersendiri dan harus diaudit.

11. Cash Closing

Sekarang sudah:

cash_adjustment
adjustment_notes

Bagus.

Tambahkan constraint seperti:

actual_cash >= 0
opening_cash >= 0
cash_sales >= 0
refunds >= 0

Dan formula:

expected_cash =
opening_cash

- cash_sales

* refunds

- cash_adjustment

Kemudian:

variance =
actual_cash - expected_cash

Saya tidak menyarankan expected_cash dan variance dihitung sembarangan dari frontend.

Backend harus menjadi sumber perhitungan.

12. RBAC

Sekarang:

users
↓
roles
↓
role_permissions
↓
permissions

Sudah bagus.

Tambahkan:

UNIQUE(role_id, permission_id)

Dan:

UNIQUE(code)

pada:

roles
permissions

Contoh:

## permissions

id
code UNIQUE
name
description
created_at
updated_at 13. Inventory Movement

Struktur:

inventory_movements
├── product_id
├── movement_type
├── quantity
├── from_location
├── to_location
├── reference_type
├── reference_id
├── actor_id
├── occurred_at
└── metadata_info

sudah bagus.

Tapi movement_type harus memiliki enum yang jelas.

Misalnya:

SALE
RECEIVING
ADJUSTMENT
STOCK_OPNAME
RETURN
OTHER

Jangan biarkan aplikasi mengirim arbitrary string:

"something"
"minus_stock"
"abc" 14. Product → GTIN

Kalau gtin adalah barcode produk:

products

- gtin

maka:

UNIQUE(gtin)

tetapi gtin boleh nullable.

Jadi:

Product A → 8991234567890
Product B → NULL
Product C → 8999876543210

Valid.

15. Nomor transaksi harus unique

Saya melihat:

sales.receipt_number
receivings.receiving_number
stock_opnames.opname_number

Ini sebaiknya unique.

Misalnya:

UNIQUE(receipt_number)
UNIQUE(receiving_number)
UNIQUE(opname_number)

Karena nomor tersebut merupakan business identifier.

16. Audit Logs

Struktur Anda sudah bagus:

audit_logs
├── actor_id
├── actor_type
├── action
├── entity_type
├── entity_id
├── before_data
├── after_data
├── metadata_info
└── timestamp

Saya hanya akan memperkuat dengan index:

INDEX(actor_id)
INDEX(entity_type, entity_id)
INDEX(timestamp)
INDEX(action)

Karena nanti query seperti:

"Siapa yang mengubah inventory Product X?"

akan sering digunakan.

Dan:

"Tampilkan seluruh aktivitas tanggal tertentu."

juga akan sering dilakukan.

17. Notifications

Saya akan tambahkan index:

INDEX(target_user_id)
INDEX(is_read)
INDEX(created_at)
INDEX(reference_type, reference_id)

Query utama nanti kemungkinan:

WHERE target_user_id = ?
AND is_read = false
ORDER BY created_at DESC

Jadi index harus mendukung pola tersebut.

🟡 P2 — Perlu dipastikan 18. events

Sekarang:

events
├── event_type
├── title
├── description
├── start_date
├── end_date
├── impact_level
├── metadata_info
└── created_at

Belum tentu salah.

Saya justru tidak menyarankan menambah kolom dulu.

Kita perlu memastikan dulu bentuk Event Intelligence yang sebenarnya.

19. ai_insights

Saat ini:

ai_insights
├── insight_type
├── title
├── summary
├── priority
├── product_id
├── evidence_data
├── recommendation
├── status
└── created_at

Ini sudah cukup bagus.

Saya hanya akan memastikan:

evidence_data → JSONB

dan status punya lifecycle jelas.

Contoh:

GENERATED
REVIEWED
DISMISSED
RESOLVED

AI juga tidak boleh menjadi source of truth inventory.

AI hanya membaca data melalui application/MCP layer dan menghasilkan insight.

20. Index FK

Jangan hanya mengandalkan PK.

FK yang sering dipakai query sebaiknya memiliki index.

Minimal:

products.category_id

inventory.product_id

inventory_movements.product_id

sale_items.sale_id
sale_items.product_id

receivings.supplier_id
receiving_items.receiving_id
receiving_items.product_id

supplier_products.supplier_id
supplier_products.product_id

warehouse_requests.product_id
warehouse_requests.requested_by_id

stock_opnames.started_by_id
stock_opname_items.product_id

inventory_closings.daily_closing_id
inventory_closing_items.product_id

cash_closings.daily_closing_id
cash_closings.cashier_id

ai_insights.product_id

notifications.target_user_id 21. Historical data — jangan hard delete

Untuk data seperti:

sales
receivings
inventory_movements
stock_opnames
daily_closings
cash_closings
audit_logs

jangan menyediakan hard delete sebagai operational flow.

Misalnya sale salah:

❌ DELETE FROM sales

lebih baik:

sale.status = VOIDED

dan buat:

audit_log

Hal yang sama berlaku untuk inventory adjustment.

Prioritas implementasi saya

Kalau Anda ingin mengerjakannya secara efisien, jangan perbaiki semuanya sekaligus.

Saya akan lakukan seperti ini:

Phase 1 — Structural
[ ] Hapus users.role
[ ] Tambahkan UNIQUE daily_closings.business_date
[ ] UNIQUE inventory_closings.daily_closing_id
[ ] UNIQUE inventory_closing_items(...)
[ ] UNIQUE stock_opname_items(...)
[ ] UNIQUE supplier_products(...)
[ ] UNIQUE receipt_number
[ ] UNIQUE receiving_number
[ ] UNIQUE opname_number
[ ] UNIQUE role.code
[ ] UNIQUE permission.code
[ ] UNIQUE role_permissions(role_id, permission_id)
Phase 2 — Data integrity
[ ] Tentukan NUMERIC precision untuk money
[ ] Tentukan precision quantity
[ ] Tambahkan CHECK constraints
[ ] Tentukan enum status
[ ] Tentukan enum movement_type
[ ] Tentukan delete policy
Phase 3 — Performance
[ ] FK indexes
[ ] Audit indexes
[ ] Notification indexes
[ ] Inventory indexes
[ ] Business-date indexes
Phase 4 — Business semantics
[ ] Finalisasi refund model
[ ] Finalisasi event model
[ ] Finalisasi AI insight lifecycle
[ ] Finalisasi closing lifecycle
[ ] Finalisasi inventory movement rules
