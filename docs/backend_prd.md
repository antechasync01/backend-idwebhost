AURA POS — Backend Product Requirements Document (Backend PRD) v2.0

## Document metadata

| Field              | Value                                                  |
| ------------------ | ------------------------------------------------------ |
| Product            | AURA POS                                               |
| Document           | Backend Product Requirements Document                  |
| Based on           | AURA POS PRD v2.0                                      |
| Backend repository | `aura-backend`                                         |
| Status             | Development Blueprint / Hackathon MVP                  |
| Architecture       | Modular Monolith                                       |
| Primary API        | FastAPI                                                |
| Database           | PostgreSQL                                             |
| AI                 | External LLM API + Internal AI Services + Hermes + MCP |

---

## 1. Backend Overview

### 1.1 Purpose

AURA Backend adalah pusat operasional dan intelligence platform AURA POS.

Backend bertanggung jawab terhadap:

- authentication
- authorization
- user & role management
- product master
- product registration
- inventory
- inventory movements
- receiving
- stock opname
- warehouse requests
- supplier management
- sales
- payment
- cash closing
- inventory closing
- daily closing
- analytics
- event intelligence
- AI services
- Hermes
- MCP
- notifications
- audit logging

Backend menjadi **single source of truth** untuk seluruh business operation.

Frontend, Tauri POS, mobile app, Hermes, dan AI **tidak boleh** memiliki business rule yang berdiri sendiri di luar backend.

---

## 2. Backend Goals

Backend AURA harus:

1. Menjaga integritas data operasional.
2. Menegakkan RBAC secara server-side.
3. Menjaga konsistensi inventory.
4. Menyediakan API yang digunakan oleh seluruh frontend.
5. Menyediakan operational data untuk analytics dan AI.
6. Menyediakan AI reasoning melalui Hermes.
7. Menjaga AI tetap berada dalam authorization boundary user.
8. Menyediakan immutable audit trail.
9. Menyediakan API yang stabil untuk Web, Mobile, dan Tauri POS.
10. Dapat dideploy sebagai satu backend container melalui Dokploy.

---

## 3. Backend Non-Goals

Backend MVP tidak mencakup:

- multi-store
- multi-tenant SaaS
- purchase order
- internal purchasing
- supplier ordering execution
- payment gateway
- QRIS
- debit
- credit
- offline-first POS
- automatic AI inventory adjustment
- automatic purchasing
- AI approval transaction
- full ERP accounting
- advanced payroll
- loyalty
- complex promotion engine
- self-hosted LLM

AURA hanya memberikan recommendation terhadap purchasing. Pembelian tetap dilakukan Owner secara eksternal.

---

## 4. Backend Architecture

### 4.1 Architecture Style

AURA Backend menggunakan **Modular Monolith** (bukan microservices).

Struktur utama:

```
aura-backend/
│
├── app/
│   ├── modules/
│   ├── mcp/
│   ├── core/
│   └── infrastructure/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── alembic/
├── Dockerfile
├── pyproject.toml
└── README.md
```

Struktur tersebut mengikuti arsitektur backend pada PRD v2.

---

## 5. Backend Layering

Setiap request mengikuti:

```
HTTP Request
     ↓
API Router
     ↓
Authentication
     ↓
Authorization
     ↓
Application / Use Case
     ↓
Domain
     ↓
Repository
     ↓
PostgreSQL / External Service
```

Business rules harus berada di:

- Domain layer
- Application layer

Business rules **tidak boleh** ditempatkan di:

- frontend
- API router
- Hermes
- MCP tool implementation

---

## 6. Backend Modules

```
app/modules/

├── auth/
├── users/
├── products/
├── inventory/
├── sales/
├── warehouse/
├── suppliers/
├── analytics/
├── events/
├── ai/
├── notifications/
└── audit/
```

Setiap module menggunakan pola:

```
module/
├── api/
├── application/
├── domain/
└── infrastructure/
```

Contoh:

```
inventory/
├── api/
│   └── inventory_router.py
│
├── application/
│   ├── transfer_display.py
│   ├── adjust_inventory.py
│   └── stock_opname.py
│
├── domain/
│   ├── inventory.py
│   ├── movement.py
│   └── exceptions.py
│
└── infrastructure/
    ├── inventory_repository.py
    └── models.py
```

---

## 7. Technology Requirements

### 7.1 Core Backend

| Component        | Technology |
| ---------------- | ---------- |
| Language         | Python     |
| API              | FastAPI    |
| Validation       | Pydantic   |
| ORM              | SQLAlchemy |
| Migration        | Alembic    |
| Database         | PostgreSQL |
| Authentication   | JWT        |
| Password hashing | Argon2id   |
| Testing          | Pytest     |
| Container        | Docker     |
| Deployment       | Dokploy    |

---

## 8. Authentication

### 8.1 Authentication Method

MVP menggunakan:

- username/email
- password
- JWT
- refresh token
- Argon2id password hashing

Flow:

```
Login
 ↓
Validate credentials
 ↓
Verify password
 ↓
Generate access token
 ↓
Generate refresh token
 ↓
Authenticated API requests
```

---

## 9. Password Security

Password:

- tidak boleh disimpan plaintext
- wajib menggunakan Argon2id
- tidak boleh dikembalikan melalui API
- tidak boleh dimasukkan ke audit log

Backend harus melakukan password verification melalui password hashing service.

---

## 10. JWT

Access token minimal membawa:

```json
{
  "sub": "user_uuid",
  "role": "OWNER",
  "token_type": "access"
}
```

Refresh token digunakan untuk mendapatkan access token baru.

Backend harus melakukan:

- token signature validation
- expiration validation
- token type validation
- user existence validation
- user active-status validation

---

## 11. RBAC

Authorization hierarchy:

```
User
 ↓
Role
 ↓
Permission
 ↓
Policy
 ↓
Application Service
```

Backend adalah security boundary.

Frontend hanya boleh menggunakan permission untuk UX visibility (visibility **bukan** security mechanism).

Unauthorized operation harus menghasilkan:

- `403 Forbidden`

---

## 12. Roles

Backend mendukung empat human roles:

- `OWNER`
- `WAREHOUSE_ADMIN`
- `WAREHOUSE_STAFF`
- `CASHIER`

AI bukan human user.

Untuk audit, AI dapat direpresentasikan sebagai:

- `actor_type = AI`

---

## 13. Permission Model (contoh)

Permission harus granular. Contoh:

```
product.read
product.create
product.update
product.approve

inventory.read
inventory.transfer
inventory.adjust

receiving.read
receiving.submit
receiving.approve
receiving.reject
receiving.request_correction

sales.create
sales.read
sales.void
sales.refund

supplier.read
supplier.create
supplier.update
supplier.link_product

analytics.read
ai.read
ai.investigate
```

Role tidak boleh langsung menentukan business behavior; role hanya digunakan untuk resolve permission.

---

## 14. Authorization per Role (ringkas)

### 14.1 Owner

Akses: dashboard, analytics, inventory intelligence, AI insights/recommendations, Hermes, events, supplier mgmt, warehouse requests, audit, settings.

Owner tidak menjalankan: receiving fisik, POS, product master creation, receiving operation.

### 14.2 Warehouse Admin

Mengelola: product master, approval workflow (product registration, receiving), inventory movement, display transfer, stock opname, inventory closing, AI insights.

Jika Admin melakukan receiving sendiri:

- Submit Receiving → Complete (tanpa approval kedua)

### 14.3 Warehouse Staff

Dapat: scan EAN-13, product lookup, submit product registration, submit receiving, inventory view, display transfer, submit stock opname, warehouse request, limited AI.

Tidak dapat: approve product/receiving, final inventory closing, inventory adjustment.

### 14.4 Cashier

Dapat: login, product lookup, create sale, cash payment, receipt, transaction history, cash closing.

Tidak punya akses Owner dashboard.

---

## 15. Product Domain

### 15.1 Product Identity

Setiap product memiliki internal UUID `id`.

External identifier:

- `EAN-13 / GTIN-13`

QR code bukan otomatis product identifier.

### 15.2 Product Entity (minimal)

```
Product
├── id
├── gtin/ean13
├── name
├── brand
├── category_id
├── unit
├── description
├── purchase_price
├── selling_price
├── status
├── external_metadata
├── created_at
└── updated_at
```

Status:

- `ACTIVE`
- `INACTIVE`
- `ARCHIVED`

### 15.3 Product Status Rules

- ACTIVE: dapat dijual dan digunakan dalam workflow.
- INACTIVE: tidak dijual sementara/permanen, data historis tetap tersedia.
- ARCHIVED: tidak relevan untuk UI operasional; histori tetap disimpan.

Backend tidak boleh hard delete product yang memiliki historical transaction.

---

## 16. Product Provider

Backend menggunakan abstraction:

```
ProductProvider
├── CSVProductProvider
├── ManualProductProvider
└── GS1ProductProvider
```

Untuk MVP, `CSV / seeded catalog` menjadi sumber utama. GS1 hanya extension point.

---

## 17. Product Registration

Jika EAN belum ditemukan:

```
Scan EAN
 ↓
Product Not Found
 ↓
Product Registration Request
 ↓
PENDING
 ↓
Warehouse Admin
 ├── APPROVE
 │     ↓
 │ Product Master
 │     ↓
 │ Inventory = 0
 │
 └── REJECT
```

Product Registration dan Receiving adalah dua domain workflow berbeda.

---

## 18. Inventory Domain

### 18.1 Stock Locations & Source of Truth

Physical stock location:

- `DISPLAY`
- `ON_HAND`

Inventory source of truth:

- `display_quantity`
- `on_hand_quantity`

Total available:

- `total_available = display_quantity + on_hand_quantity` (derived, tidak disimpan).

### 18.2 Inventory Invariant

Invariant utama:

```
Total Available
=
Display Quantity
+
On Hand Quantity
```

Transfer internal tidak boleh mengubah total inventory.

### 18.3 Inventory Transaction Integrity

Setiap inventory mutation wajib dalam database transaction. Contoh:

```
BEGIN

validate permission
validate product
validate quantity
validate source stock
update inventory
create inventory movement
create audit log

COMMIT
```

Jika gagal: `ROLLBACK`.

Tidak boleh terjadi mismatch:

- inventory updated tapi movement missing, atau sebaliknya.

---

## 19. Inventory Movement

Movement types:

- PURCHASE_RECEIVING
- SALE
- RETURN
- ADJUSTMENT
- DAMAGE
- EXPIRY
- DISPLAY_TRANSFER
- STOCK_OPNAME

Entity minimal:

```
inventory_movements
├── id
├── product_id
├── movement_type
├── quantity
├── from_location
├── to_location
├── reference_type
├── reference_id
├── actor_id
├── occurred_at
└── metadata
```

---

## 20. Display Transfer

Transfer:

- `DISPLAY ↔ ON_HAND`

Tidak membutuhkan approval.

Flow:

```
Select Product
 ↓
Input Quantity
 ↓
Validate source stock
 ↓
Decrease source
 ↓
Increase destination
 ↓
Create Movement
 ↓
Create Audit Log
```

---

## 21. Sale & Inventory

MVP menetapkan:

- `SALE` mengurangi `DISPLAY` stock.

Jika display tidak cukup, warehouse harus melakukan transfer `ON_HAND → DISPLAY` melalui display transfer.

Backend tidak boleh auto-transfer inventory pada saat sale terjadi.

---

## 22. Receiving Domain

Receiving default masuk ke:

- `ON_HAND`

Flow:

```
Warehouse Staff
 ↓
Submit Receiving
 ↓
PENDING
 ↓
Warehouse Admin
 ↓
APPROVE
 ↓
Inventory + quantity
 ↓
Inventory Movement
```

State machine:

```
DRAFT
  ↓
PENDING
  ├── APPROVED
  ├── REJECTED
  └── CORRECTION_REQUESTED
```

Approval wajib membuat:

- inventory mutation
- movement
- audit event

(semua dalam satu transaction)

---

## 23. Receiving Correction

Jika Staff salah input:

```
PENDING
 ↓
Admin
 ├── APPROVE
 ├── REJECT
 └── REQUEST_CORRECTION
```

`REQUEST_CORRECTION` lebih disukai untuk menjaga auditability.

---

## 24. Stock Opname

Workflow terpisah dari Daily Closing.

Yang dihitung:

- Physical Display
- Physical On Hand

Flow:

```
Staff/Admin
 ↓
Start Stock Opname
 ↓
Count Physical Stock
 ↓
Submit
 ↓
Warehouse Admin
 ↓
Final Approval
```

Variance tidak otomatis menjadi adjustment.

---

## 25. Variance Handling & Adjustment

Variance state:

- `NEEDS_REVIEW`

Flow:

```
Variance
 ↓
NEEDS_REVIEW
 ↓
Human Investigation
 ↓
Decision
 ├── NO_ACTION
 └── INVENTORY_ADJUSTMENT
```

Inventory adjustment adalah critical mutation dan hanya role ber-permission `inventory.adjust` yang boleh. AI tidak boleh melakukan adjustment.

---

## 26. Warehouse Request

Warehouse dapat membuat request kepada Owner.

Flow:

```
Warehouse
 ↓
Warehouse Request
 ↓
Owner
 ↓
Review
 ↓
External Purchasing
```

AURA tidak melakukan purchasing.

---

## 27. Supplier Domain

Supplier hanya dikelola Owner.

Entity minimal:

```
suppliers
├── id
├── name
├── contact_person
├── phone
├── whatsapp
├── address
├── notes
├── created_at
└── updated_at
```

Relationship:

- Supplier → Supplier Products → Product

---

## 28. Purchasing Boundary

Backend tidak menyediakan:

- purchase orders
- supplier order execution

AI hanya:

Need detected → recommendation → supplier info → owner → external purchase.

---

## 29. Sales Domain

Sales flow:

```
Product Lookup
 ↓
Cart
 ↓
Cash Payment
 ↓
Sale Created
 ↓
Inventory Reduced
 ↓
Receipt
```

MVP hanya mendukung cash payment.

Create sale harus atomic (sale + items + inventory mutation + movement + audit).

---

## 30. Cash Closing, Inventory Closing, Daily Closing

### 30.1 Cash Closing

Cash reconciliation:

```
Opening Cash
+ Cash Sales
- Refunds
± Cash Adjustment
=
Expected Cash
```

Cash variance:

```
Actual Cash - Expected Cash
```

Normal cash closing tidak membutuhkan approval Owner.

### 30.2 Inventory Closing

Bagian dari Daily Closing; tidak semua SKU harus dihitung. Selection dapat berasal dari:

- selected products
- low-stock products
- high-risk products
- random sampling

Full Stock Opname tetap workflow terpisah.

### 30.3 Daily Closing

Daily Closing adalah parent process:

```
Daily Closing
├── Cash Closing
└── Inventory Closing
```

---

## 31. Analytics

Analytics membaca operational data dan menyediakan business metrics (read-only).

Minimum metrics:

- Sales: revenue, units sold, sales by product/category, trend, daily/weekly comparison
- Inventory: current stock, low stock, movement, turnover, stockout risk
- Business: best sellers, slow movers, demand trend, event impact

---

## 32. AI Architecture

AI layer:

- AI Services: Demand Forecast, Stockout Risk, Anomaly Detection, Event Intelligence, Recommendation
- Hermes: Reasoning, Tool Calling, Investigation, Explanation, Conversation

### 32.1 AI Priority (Hackathon)

Tier 1:

1. Demand Forecast
2. Stockout Risk
3. Event Intelligence
4. Reorder Recommendation

---

## 33. Hermes & MCP

### 33.1 Hermes

Conversational reasoning/orchestration layer.

Flow:

```
User Question
 ↓
Intent Understanding
 ↓
MCP Tools
 ↓
Operational Data
 ↓
Analysis
 ↓
Evidence
 ↓
Explanation
```

### 33.2 Hermes Authorization (Non-negotiable)

Hermes inherits authorization context dari current user:

- Owner → Hermes → MCP → Owner permissions
- Cashier → Hermes → MCP → Cashier permissions

AI tidak mendapatkan privilege tambahan.

### 33.3 MCP Architecture

```
Hermes
 ↓
MCP Gateway
 ↓
Tool Registry (whitelist)
 ↓
Permission / Scope Check
 ↓
Application Service
 ↓
Domain
 ↓
PostgreSQL
```

Dilarang:

- Hermes → PostgreSQL (direct)

Tidak ada critical mutation tool.

---

## 34. External LLM API

Backend adalah satu-satunya layer yang berkomunikasi dengan external LLM.

Dilarang:

- Frontend → LLM provider

LLM tidak mendapatkan:

- DB credentials
- direct database connection
- unrestricted internal API
- user secrets

---

## 35. Notifications

AI bukan Notification Service.

Flow:

```
AI
 ↓ Detect risk
AI Insight
 ↓
Notification Service
 ↓
Recipient
```

Notification types (MVP):

- AI_INSIGHT
- STOCKOUT_RISK
- LOW_STOCK
- ANOMALY
- WAREHOUSE_REQUEST
- CLOSING_VARIANCE
- PRODUCT_REQUEST
- RECEIVING_PENDING

---

## 36. Audit System

Centralized audit table.

Actor categories:

- OWNER
- WAREHOUSE_ADMIN
- WAREHOUSE_STAFF
- CASHIER
- AI

Audit log harus immutable. Koreksi dilakukan melalui event baru (bukan update).

---

## 37. Database (PostgreSQL)

Core tables (baseline):

- users
- products
- categories
- inventory
- inventory_movements
- product_registration_requests
- receivings
- receiving_items
- sales
- sale_items
- suppliers
- supplier_products
- warehouse_requests
- daily_closings
- cash_closings
- inventory_closings
- stock_opnames
- audit_logs
- events
- ai_insights
- notifications

Design principles:

- UUID primary identifiers
- FK constraints
- database transaction untuk critical mutation
- indexes untuk lookup
- timestamps
- hindari hard delete untuk historical data

---

## 38. Inventory Concurrency

Inventory mutation harus aman terhadap concurrent request.

Minimal gunakan:

- `SELECT ... FOR UPDATE`

untuk mencegah race condition (mis. dua sale bersamaan pada stock terbatas).

---

## 39. API Architecture

API versioning:

- `/api/v1`

Grouping baseline (dapat disesuaikan saat implementasi):

- /api/v1/auth
- /api/v1/users
- /api/v1/products
- /api/v1/product-registration
- /api/v1/inventory
- /api/v1/inventory-movements
- /api/v1/stock-opname
- /api/v1/receivings
- /api/v1/sales
- /api/v1/daily-closing
- /api/v1/cash-closing
- /api/v1/inventory-closing
- /api/v1/suppliers
- /api/v1/warehouse-requests
- /api/v1/analytics
- /api/v1/events
- /api/v1/ai
- /api/v1/hermes
- /api/v1/audit

---

## 40. Response, Errors, and HTTP Status

Response envelope (contoh):

Success:

```json
{ "data": {}, "meta": {} }
```

Error:

```json
{
  "error": {
    "code": "INVENTORY_INSUFFICIENT",
    "message": "Insufficient display stock."
  }
}
```

HTTP status minimal:

- 200, 201, 204
- 400, 401, 403, 404, 409, 422
- 500

Gunakan `409 Conflict` untuk domain conflict (insufficient stock, invalid state transition, duplicate transaction, already finalized closing).

---

## 41. Business Date

Backend harus membedakan:

- `created_at` (timestamp)
- `business_date` (operational reporting reference)

Timezone store harus dikonfigurasi eksplisit.

---

## 42. Idempotency

Critical endpoint yang berpotensi menerima duplicate request harus mendukung idempotency (mis. `Idempotency-Key`), terutama:

- POST /sales
- POST /receivings
- POST /cash-closing
- POST /inventory-closing

Tujuan: retry karena network issue tidak membuat transaksi ganda.

---

## 43. External Service Isolation & Failure

External integrations diisolasi pada infrastructure layer (llm/weather/events/product_provider).

External API failure harus graceful degradation: core POS operations (sale, transfer, receiving, closing) tidak boleh gagal hanya karena intelligence provider unavailable.

---

## 44. Redis (Optional)

Redis bersifat optional dan tidak boleh menjadi dependency wajib untuk core operation.

Jika digunakan:

- caching
- temporary state
- rate limiting
- future background jobs

PostgreSQL tetap source of truth.

---

## 45. Testing Strategy

Testing dibagi:

- unit
- integration
- e2e

Wajib menguji business rules & integrity:

- inventory calculation & invariant
- display transfer
- stockout calculation
- closing calculation
- permission policy
- recommendation logic
- concurrency (simultaneous sales)
- audit immutability
- MCP tool permission + scope validation

---

## 46. Deployment (Docker + Dokploy)

Backend harus bisa:

- `docker build`
- `docker run`

Container harus stateless, configurable via env vars, expose HTTP API, punya healthcheck.

Deployment server-side via Dokploy + reverse proxy + HTTPS.

MCP berada di backend yang sama (bukan container terpisah).

---

## 47. Environment Variables (minimal)

- DATABASE_URL
- JWT_SECRET
- JWT_ACCESS_EXPIRE
- JWT_REFRESH_EXPIRE
- LLM_API_KEY
- LLM_BASE_URL
- LLM_MODEL
- WEATHER_API_KEY
- EXTERNAL_EVENT_API_KEY
- CORS_ORIGINS

Secrets tidak boleh disimpan di repository.

---

## 48. Recommended Repository Structure (Final)

```
aura-backend/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── core/                         # Shared application infrastructure
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── permissions.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   │
│   ├── modules/                      # Business domains
│   │   │
│   │   ├── auth/
│   │   │   ├── api/
│   │   │   ├── application/
│   │   │   ├── domain/
│   │   │   └── infrastructure/
│   │   │
│   │   ├── users/
│   │   │   ├── api/
│   │   │   ├── application/
│   │   │   ├── domain/
│   │   │   └── infrastructure/
│   │   │
│   │   ├── products/
│   │   │   ├── api/
│   │   │   ├── application/
│   │   │   ├── domain/
│   │   │   └── infrastructure/
│   │   │
│   │   ├── inventory/
│   │   │   ├── api/
│   │   │   ├── application/
│   │   │   ├── domain/
│   │   │   └── infrastructure/
│   │   │
│   │   ├── sales/
│   │   │   ├── api/
│   │   │   ├── application/
│   │   │   ├── domain/
│   │   │   └── infrastructure/
│   │   │
│   │   ├── warehouse/
│   │   ├── suppliers/
│   │   ├── analytics/
│   │   ├── events/
│   │   ├── ai/
│   │   ├── notifications/
│   │   └── audit/
│   │
│   ├── mcp/                          # AI tool gateway
│   │   ├── gateway.py
│   │   ├── registry.py
│   │   ├── context.py
│   │   └── tools/
│   │       ├── read/
│   │       ├── analyze/
│   │       └── recommend/
│   │
│   └── infrastructure/               # External/shared adapters
│       ├── llm/
│       ├── weather/
│       ├── events/
│       └── product_provider/
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── scripts/
│   ├── seed.py
│   └── bootstrap.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── alembic.ini
├── .env.example
└── README.md
```

## 48.1 Module Layering & Internal Responsibility

Setiap business module pada AURA Backend menggunakan struktur berlapis:

module/
├── api/
├── application/
├── domain/
└── infrastructure/

Struktur ini digunakan untuk menjaga separation of concerns, menjaga business rule tetap berada di backend, dan mencegah coupling antara business logic dengan framework atau teknologi persistence.

Alur request secara umum:

HTTP Request
↓
API
↓
Authentication
↓
Authorization
↓
Application
↓
Domain
↓
Infrastructure
↓
PostgreSQL / External Service

Business rules harus berada pada Application dan Domain layer. Business rules tidak boleh ditempatkan di API Router, frontend, Hermes, atau MCP tool implementation.

## 48.2 API Layer

API layer bertanggung jawab terhadap komunikasi antara backend dan external client seperti:

Expo Web
Expo Mobile
Tauri POS
MCP internal interface apabila menggunakan application API

Tanggung jawab utama:

menerima HTTP request
melakukan request validation menggunakan Pydantic
parsing request parameter
authentication dependency
authorization dependency
memanggil application service/use case
mengubah application result menjadi HTTP response
menentukan HTTP status code

API layer tidak boleh menjalankan business logic atau melakukan operasi database secara langsung.

Contoh struktur:

inventory/
└── api/
├── router.py
├── schemas.py
└── dependencies.py

Contoh alur:

POST /api/v1/inventory/transfer
↓
inventory/api/router.py
↓
TransferStockUseCase

API hanya bertugas sebagai entry point untuk request.

## 48.2 Application Layer

Application layer merepresentasikan use case atau application operation.

Application layer bertanggung jawab untuk mengorkestrasi proses bisnis dengan menggabungkan authorization, domain logic, repository, transaction, dan service lainnya.

Contoh use case:

Transfer Stock
Adjust Inventory
Create Sale
Submit Receiving
Approve Receiving
Submit Stock Opname
Finalize Closing
Generate AI Insight

Contoh struktur:

inventory/
└── application/
├── transfer_stock.py
├── adjust_inventory.py
├── stock_opname.py
└── get_inventory.py

Application layer bertanggung jawab terhadap:

menjalankan use case
memastikan authorization sudah terpenuhi
mengambil data melalui repository
mengoordinasikan domain objects
menjalankan database transaction untuk critical mutation
membuat atau memperbarui entity melalui domain rules
membuat inventory movement
membuat audit event
melakukan commit atau rollback transaction

Contoh flow Transfer Stock:

TransferStockUseCase
↓
Check Permission
↓
Load Inventory
↓
Lock Inventory Row
↓
Execute Domain Rule
↓
Update Inventory
↓
Create Inventory Movement
↓
Create Audit Log
↓
Commit Transaction

Critical mutation seperti sale, receiving, transfer, dan closing harus dijalankan secara atomic dalam database transaction.

Application layer merupakan orchestrator, bukan tempat untuk menyimpan seluruh business rule secara langsung.

## 48.3 Domain Layer

Domain layer berisi business rule inti AURA yang harus tetap valid terlepas dari bagaimana sistem dipanggil.

Domain layer tidak bergantung pada:

FastAPI
HTTP
PostgreSQL
SQLAlchemy
Redis
External API
LLM provider
MCP transport

Domain layer merepresentasikan:

domain entity
value object apabila diperlukan
domain rules
domain policy
domain exception
invariant

Contoh struktur:

inventory/
└── domain/
├── inventory.py
├── movement.py
├── policies.py
└── exceptions.py

Contoh business rule inventory:

1. display_quantity tidak boleh negatif.
2. on_hand_quantity tidak boleh negatif.
3. SALE hanya mengurangi DISPLAY stock.
4. DISPLAY_TRANSFER tidak mengubah total available stock.
5. Inventory adjustment merupakan critical mutation.
6. Total available = display_quantity + on_hand_quantity.

Contoh implementasi konseptual:

class Inventory:

    def transfer_to_display(self, quantity):
        if quantity <= 0:
            raise InvalidQuantity()

        if self.on_hand_quantity < quantity:
            raise InsufficientStock()

        self.on_hand_quantity -= quantity
        self.display_quantity += quantity

Aturan tersebut harus tetap berlaku ketika operation dipanggil melalui:

Web
Mobile
Tauri POS
Internal Application Service
MCP

Hal ini memastikan backend tetap menjadi single source of truth dan Hermes/MCP tidak dapat melewati business rules backend.

## 48.4 Infrastructure Layer

Infrastructure layer bertanggung jawab terhadap implementasi teknis yang digunakan untuk mengakses persistence dan external system.

Infrastructure layer dapat berisi:

SQLAlchemy models
repository implementation
database queries
PostgreSQL-specific implementation
external API client
cache adapter
provider implementation
persistence mapping

Contoh:

inventory/
└── infrastructure/
├── models.py
├── inventory_repository.py
└── movement_repository.py

Contoh tanggung jawab:

InventoryRepository
↓
SQLAlchemy
↓
PostgreSQL

Infrastructure layer mengetahui detail teknis seperti:

select(...)
insert(...)
update(...)
session.add(...)
session.execute(...)

Business layer tidak boleh bergantung langsung pada detail SQLAlchemy atau PostgreSQL.

External integrations juga ditempatkan pada infrastructure layer sehingga kegagalan external provider tidak boleh menyebabkan core POS operations gagal.

## 48.5 Dependency Rules

AURA Backend harus mengikuti dependency direction berikut:

API
↓
Application
↓
Domain

Infrastructure
↓
implements persistence / external adapter

Aturan:

API boleh bergantung pada Application.
Application boleh menggunakan Domain.
Application boleh menggunakan abstraction/interface repository.
Infrastructure mengimplementasikan repository dan adapter yang dibutuhkan Application.
Domain tidak boleh bergantung pada FastAPI, SQLAlchemy, PostgreSQL, atau external service.
API tidak boleh mengakses database secara langsung.
MCP tidak boleh mengakses PostgreSQL secara langsung.
Hermes tidak boleh mengakses PostgreSQL secara langsung.
Semua critical business mutation harus melewati Application Service dan Domain layer.

Architecture AURA menetapkan alur Hermes/MCP sebagai:

Hermes
↓
MCP Gateway
↓
Tool Registry
↓
Permission / Scope Check
↓
Application Service
↓
Domain
↓
PostgreSQL

Hermes dan MCP tidak boleh melakukan direct database access.

## 48.6 SQLAlchemy Model Placement

SQLAlchemy ORM model ditempatkan pada Infrastructure layer dari module yang memiliki domain tersebut.

Contoh:

products/
└── infrastructure/
└── models.py

inventory/
└── infrastructure/
└── models.py

sales/
└── infrastructure/
└── models.py

receivings/
└── infrastructure/
└── models.py

suppliers/
└── infrastructure/
└── models.py

Tidak menggunakan global model directory seperti:

app/models/

karena setiap business domain harus memiliki ownership terhadap persistence model-nya.

Contoh:

inventory/
├── api/
├── application/
├── domain/
└── infrastructure/
├── models.py
└── inventory_repository.py

Dengan pola ini, database model tetap dekat dengan domain yang mengelolanya.

## 48.7 Example: Create Sale

Contoh implementasi Create Sale mengikuti layering berikut:

Tauri POS
↓
POST /api/v1/sales
↓
sales/api/router.py
↓
CreateSaleUseCase
↓
Authorization
↓
Load Product
↓
Lock Inventory
↓
Sale Domain
↓
Validate Payment
↓
Validate Inventory
↓
Create Sale
↓
Create Sale Items
↓
Decrease DISPLAY Stock
↓
Create Inventory Movement
↓
Create Audit Log
↓
Commit Transaction
↓
HTTP Response

Dengan demikian:

API
= menerima request

Application
= mengorkestrasi use case

Domain
= memastikan business rule

Infrastructure
= menyimpan dan mengambil data
5.X.8 Layer Responsibility Summary
Layer Tanggung Jawab Tidak Boleh
API HTTP, request/response, validation, dependency Business logic, direct DB
Application Use case, orchestration, transaction HTTP-specific logic
Domain Business rule, invariant, entity, policy FastAPI, SQLAlchemy, DB
Infrastructure ORM, repository, DB, external adapter Business orchestration
Prinsip utama
API
"Bagaimana request masuk?"

Application
"Use case apa yang sedang dijalankan?"

Domain
"Apa yang diperbolehkan oleh bisnis?"

Infrastructure
"Bagaimana data/service tersebut diakses?"

## Struktur ini mempertahankan Modular Monolith AURA sekaligus memberikan batas yang jelas antar-layer. Setiap module tetap memiliki api, application, domain, dan infrastructure sehingga business logic dapat berkembang tanpa membuat API, database, dan external integrations saling tightly coupled. Ini konsisten dengan arsitektur modular monolith dan pola module yang sudah ditetapkan dalam PRD AURA.

## 49. Definition of Done — Backend MVP (ringkas)

Backend selesai untuk demo jika:

- Auth + RBAC jalan (403 untuk unauthorized)
- Product master + product registration workflow jalan
- Inventory konsisten (DISPLAY + ON_HAND), movement tercatat, concurrency aman
- Receiving + approval + correction request jalan
- Stock opname + variance review flow jalan (tanpa auto-adjustment)
- Sale + cash payment jalan, atomic + audit
- Closing (cash/inventory/daily) dasar jalan
- Supplier + supplier-product relation untuk reorder context
- Analytics minimum tersedia
- AI tier-1 demoable (forecast → stockout risk → recommendation) dengan evidence
- Hermes + MCP jalan dengan authorization inheritance
- Docker + Dokploy deployment siap, Postgres persistent

---

## 50. Critical Architectural Rules (NON-NEGOTIABLE)

1. Backend owns business rules (frontend/Hermes bukan authority)
2. AI never bypasses backend (Hermes → MCP → App Service → Domain → DB)
3. No critical mutation through AI
4. Inventory has one source of truth (DISPLAY + ON_HAND)
5. Total available derived (Display + On Hand)
6. Audit immutable (correction = new event)
7. Purchasing external (AURA recommends, owner acts)
8. PostgreSQL is source of truth
9. Single store MVP
10. Modular monolith boundaries jelas

---

## 51. Development Roadmap

Roadmap pelaksanaan pengembangan AURA POS Backend terbagi menjadi 6 fase terstruktur:

### Phase 1: Core Foundation & Infrastructure Setup (Day 1)

- **Fokus:** Setup database, environment, core framework, authentication (JWT + Argon2id), RBAC, serta database seeding.
- **Deliverables:**
  - Config, Database Connection (`app/core/database.py`), dan Docker Compose Postgres setup ✅
  - Schema Migration dengan Alembic (`alembic/versions/`) ✅
  - Core Modules (`app/core/`): Exception handlers, standard response format, security utils.
  - Auth & User Module (`app/modules/auth/`, `app/modules/users/`):
    - Endpoint `POST /api/v1/auth/login` (access & refresh token)
    - RBAC Dependency (`Owner`, `Warehouse Admin`, `Warehouse Staff`, `Cashier`)
  - Database Seeder Script (`scripts/seed.py`) untuk data awal User, Kategori, dan Produk.

### Phase 2: Product Master & Inventory Foundations (Day 1 - Day 2)

- **Fokus:** Pengelolaan katalog produk, workflow pendaftaran produk baru, serta kontrol lokasi inventori (`DISPLAY` & `ON_HAND`).
- **Deliverables:**
  - Products Module (`app/modules/products/`):
    - CRUD Produk & Kategori (`GET/POST/PUT /api/v1/products`)
    - Lookup EAN-13 / GTIN (`GET /api/v1/products/lookup/{gtin}`)
  - Product Registration Workflow (`app/modules/product-registration/`):
    - Submission request pendaftaran produk oleh Staff
    - Approval / Rejection oleh Warehouse Admin
  - Inventory Module (`app/modules/inventory/`):
    - API pembacaan stok (`GET /api/v1/inventory`)
    - Internal Display Transfer (`POST /api/v1/inventory/transfer` - `ON_HAND` ↔ `DISPLAY`)
    - Concurrency safety (`SELECT ... FOR UPDATE`) dan pencatatan transaksi mutasi (`inventory_movements`).

### Phase 3: Operational Workflows (Receiving, Sales & Stock Opname) (Day 2 - Day 3)

- **Fokus:** Workflow operasional utama toko: penerimaan barang, transaksi penjualan (POS), stock opname, dan pengajuan ke Owner.
- **Deliverables:**
  - Warehouse Receiving (`app/modules/warehouse/`, `app/modules/receivings/`):
    - Form penerimaan barang (`POST /api/v1/receivings`)
    - Admin approval, rejection, dan correction request workflow
    - Transaksi mutasi stok otomatis saat disetujui (`ON_HAND`).
  - Sales & POS Module (`app/modules/sales/`):
    - Pencatatan transaksi kasir (`POST /api/v1/sales`) dengan dukungan header `Idempotency-Key`
    - Eksekusi transaksi atomik (pengurangan stok `DISPLAY`, pembuat item penjualan, mutasi stok, dan audit log).
  - Stock Opname & Variance Review (`app/modules/stock-opname/`):
    - Input penghitungan stok fisik
    - Deteksi selisih (`NEEDS_REVIEW`) dan penyesuaian inventori manual (`INVENTORY_ADJUSTMENT`).
  - Supplier & Warehouse Request (`app/modules/suppliers/`, `app/modules/warehouse-requests/`):
    - Manajemen Supplier dan pengikatan produk
    - Pengajuan stok barang gudang ke Owner.

### Phase 4: Closing Operations & Immutable Audit System (Day 3 - Day 4)

- **Fokus:** Rekonsiliasi penutupan toko harian dan penegakan sistem audit immutable.
- **Deliverables:**
  - Cash Closing (`POST /api/v1/cash-closing`): Perhitungan saldo kas fisik vs sistem dan selisih kas.
  - Inventory Closing (`POST /api/v1/inventory-closing`): Uji petik produk risiko tinggi/stok rendah.
  - Daily Closing Consolidation (`POST /api/v1/daily-closing`): Penutupan harian toko.
  - Audit System (`app/modules/audit/`): Centralized immutable audit logger untuk seluruh aksi mutasi dan aktivitas AI.

### Phase 5: AI Engine, Hermes Reasoning & MCP Integration (Day 4 - Day 5)

- **Fokus:** Integrasi layanan prediktif AI, Hermes conversational reasoning agent, dan MCP Tools.
- **Deliverables:**
  - AI Services (`app/modules/ai/`):
    - Demand Forecast, Stockout Risk Calculation, Anomaly Detection, dan Event Intelligence
    - Insight Generator dan pembuatan notifikasi (`app/modules/notifications/`).
  - MCP Architecture (`app/mcp/`):
    - MCP Gateway, Registry, dan Context-aware execution
    - Implementasi Read-only MCP Tools untuk Hermes (lookup stok, ringkasan penjualan, riskan stok).
  - Hermes Agent (`app/modules/hermes/`):
    - Chat Reasoning API (`POST /api/v1/hermes/chat`)
    - Inherit JWT Authorization Context user yang memanggil (strict security boundary).

### Phase 6: Analytics, Deployment & End-to-End Verification (Day 5)

- **Fokus:** Analytics dashboard API, pengujian otomatis, kontainerisasi Docker, dan deployment Dokploy.
- **Deliverables:**
  - Analytics Module (`app/modules/analytics/`): Metrik penjualan, tren produk laris/lambat, dan turnover inventori.
  - Testing Suite (`tests/`): Unit testing business invariants & E2E integration test scenario.
  - Production Build: `Dockerfile` final, pengujian `docker compose`, dan persiapan deployment Dokploy.
