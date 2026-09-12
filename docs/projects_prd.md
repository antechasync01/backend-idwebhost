AURA POS — Product Requirements Document (PRD) v2.0

## Document metadata

| Field            | Value                                                         |
| ---------------- | ------------------------------------------------------------- |
| Product          | AURA POS                                                      |
| Product type     | AI-Native Minimarket Operating & Decision Intelligence System |
| Target           | Single minimarket / single store                              |
| Document version | 2.0                                                           |
| Status           | Development Blueprint / Hackathon MVP                         |

---

## 1. Product Overview

AURA POS adalah sistem operasional minimarket yang menggabungkan **POS**, **inventory**, **warehouse operations**, **analytics**, **event intelligence**, dan **AI decision support** dalam satu platform.

AURA tidak hanya mencatat apa yang terjadi di toko, tetapi membantu Owner memahami:

- apa yang sedang terjadi,
- mengapa hal tersebut terjadi,
- apa yang kemungkinan akan terjadi,
- tindakan apa yang sebaiknya dilakukan.

### Core intelligence loop (AURA)

OBSERVE

↓

UNDERSTAND

↓

PREDICT

↓

RECOMMEND

↓

HUMAN DECISION

↓

REAL-WORLD ACTION

AI/Hermes berada pada bagian **Understand → Predict → Recommend**, sedangkan keputusan bisnis dan tindakan nyata tetap berada pada manusia.

---

## 2. Product Vision

AURA membantu pemilik minimarket mengambil keputusan lebih cepat dan lebih baik dengan mengubah data operasional toko menjadi **actionable intelligence**.

AURA harus mampu menjawab pertanyaan seperti:

- “Produk apa yang akan habis minggu depan?”
- “Kenapa penjualan Aqua turun?”
- “Kenapa stok fisik berbeda dengan sistem?”
- “Apa yang harus saya perhatikan hari ini?”
- “Apakah event akhir pekan akan meningkatkan kebutuhan produk tertentu?”
- “Supplier mana yang harus saya hubungi?”

Namun AURA **tidak mengambil alih** kontrol operasional manusia.

---

## 3. Product Philosophy

### 3.1 AI sebagai Decision Intelligence

AURA bukan ERP yang diberi chatbot.

AI harus menjadi **intelligence layer** di atas **operational system**:

- **Operational System**: POS / Inventory / Warehouse / Sales
- **Intelligence Layer**: Forecast / Anomaly / Recommendation / Hermes
- **Human Decision** → **Real-world Action**

---

## 4. Product Scope

### 4.1 In Scope — MVP

#### Operational

- Authentication
- RBAC

#### Product Master

- EAN-13 / GTIN-13
- Product catalog bootstrap

#### Inventory

- Display stock
- On-hand stock
- Inventory movements
- Product registration workflow
- Receiving workflow
- Display transfer
- Stock opname
- Warehouse requests
- Supplier management

#### POS

- Cash payment

#### Sales

- Daily closing
- Audit log

#### Intelligence

- Sales analytics
- Demand forecasting
- Stockout risk
- Reorder recommendation
- Sales anomaly
- Inventory anomaly
- Event intelligence
- AI investigation
- Hermes conversational assistant
- AI-generated insights
- AI notifications

#### Infrastructure

- FastAPI
- PostgreSQL
- MCP
- External LLM API
- Docker
- Dokploy
- Expo Web
- Expo Mobile
- Tauri Windows POS

---

## 5. Out of Scope — MVP

Hal-hal berikut tidak menjadi bagian MVP:

- Multi-store
- Multi-tenant SaaS
- Internal purchasing
- Purchase Order
- Supplier ordering execution
- Payment gateway
- QRIS
- Debit
- Credit
- Offline-first POS
- Automatic inventory adjustment oleh AI
- Automatic purchase oleh AI
- AI approval transaction
- Full ERP accounting
- Advanced payroll
- Loyalty program
- Complex promotion engine
- Self-hosted LLM

---

## 6. User Roles

AURA memiliki empat human roles:

- OWNER
- WAREHOUSE_ADMIN
- WAREHOUSE_STAFF
- CASHIER

AI/Hermes bukan human user.

Untuk audit, AI dapat direpresentasikan sebagai:

- `actor_type = AI`

---

## 7. Role Responsibilities

### 7.1 Owner

Owner bertanggung jawab terhadap keputusan bisnis.

**Akses:**

- Dashboard
- Sales analytics
- Inventory intelligence
- AI insights
- AI recommendations
- Hermes
- Events
- Supplier management
- Warehouse requests
- Audit logs
- Settings

**Owner tidak:**

- menerima barang secara fisik,
- menjalankan POS,
- membuat Product Master,
- melakukan stock receiving sebagai warehouse operator.

Owner melakukan pembelian di luar AURA.

### 7.2 Warehouse Admin

Warehouse Admin bertanggung jawab atas kontrol warehouse.

**Akses:**

- Inventory
- Product Master
- Product registration approval
- Receiving approval
- Inventory movement
- Display transfer
- Stock opname
- Inventory closing
- Warehouse requests
- AI insights

Warehouse Admin dapat melakukan receiving sendiri.

Jika Admin yang melakukan receiving:

- Admin → Submit Receiving → Complete

Tidak diperlukan approval kedua.

### 7.3 Warehouse Staff

Warehouse Staff menjalankan aktivitas warehouse.

**Akses:**

- Scan EAN-13
- Product lookup
- Product registration request
- Receiving submission
- Inventory view
- Display transfer
- Stock opname submission
- Warehouse request
- Limited AI insight

**Staff tidak dapat:**

- membuat Product Master langsung,
- approve product,
- approve receiving,
- melakukan final inventory closing,
- melakukan inventory adjustment.

### 7.4 Cashier

Cashier memiliki interface khusus POS Windows.

**Akses:**

- Login
- Scan/search product
- Cart
- Cash payment
- Create sale
- Receipt
- Transaction history
- Cash closing

Cashier tidak memiliki akses Owner Dashboard.

---

## 8. RBAC

Authorization menggunakan:

User

↓

Role

↓

Permission

↓

Policy

↓

Application Service

Frontend hanya mengontrol visibility UX. Security sebenarnya dilakukan backend.

Frontend

↓

API

↓

Authentication

↓

Authorization

↓

Application Service

Unauthorized request menghasilkan:

- `403 Forbidden`

---

## 9. Authentication

MVP menggunakan:

- Username/email
- Password
- JWT
- Refresh token
- Argon2id password hashing

**Flow:**

Login

↓

Verify credentials

↓

Generate JWT

↓

Frontend session

↓

Authenticated API

Tauri dapat menggunakan secure OS storage untuk credential/session persistence pada tahap implementasi.

---

## 10. Product Management

### 10.1 Product Identity

Setiap produk memiliki:

- Internal ID

AURA Product ID:

- UUID

External ID:

- EAN-13 / GTIN-13

EAN-13 digunakan sebagai identifier produk/trade item.

QR code tidak dianggap otomatis sebagai product ID.

---

## 11. Product Master

Model konseptual:

- Product
  - id
  - gtin/ean13
  - name
  - brand
  - category
  - unit
  - description
  - purchase_price
  - selling_price
  - status
  - external_metadata
  - created_at
  - updated_at

**Status:**

- `ACTIVE` — Produk aktif dan dapat dijual.
- `INACTIVE` — Produk tidak dijual untuk sementara/permanen tetapi data historis tetap tersedia.
- `ARCHIVED` — Produk sudah tidak relevan untuk operational UI tetapi histori tetap dipertahankan.

Data historis tidak dihapus.

---

## 12. Product Provider

AURA menggunakan abstraction:

- ProductProvider
  - CSVProductProvider
  - ManualProductProvider
  - GS1ProductProvider

Interface:

```python
class ProductProvider:
    def get_product_by_gtin(self, gtin: str):
        raise NotImplementedError

    def search_products(self, query: str):
        raise NotImplementedError
```

Untuk hackathon:

- CSV / seeded catalog menjadi sumber utama.
- GS1 disiapkan sebagai extension point dan tidak bergantung pada asumsi bahwa API publik tertentu tersedia.

---

## 13. Product Registration Workflow

Jika warehouse scan produk yang belum dikenal:

Staff

↓

Scan EAN-13

↓

Product Unknown

↓

Product Registration Request

↓

PENDING

↓

Warehouse Admin

- APPROVE
  ↓
  Product Master
  ↓
  Inventory = 0  

- REJECT

Product Registration berbeda dari Receiving.

---

## 14. Inventory Model

AURA menggunakan dua physical stock location:

- DISPLAY
- ON_HAND

Inventory:

- `display_quantity`
- `on_hand_quantity`

Total:

- `total_available = display_quantity + on_hand_quantity`

`total_available` tidak disimpan sebagai source of truth.

Contoh:

- Display = 24
- On Hand = 76
- Total Available = 100

---

## 15. Inventory Invariant

AURA harus menjaga:

Total Available

=

Display Quantity

-

On Hand Quantity

Transfer internal tidak mengubah total stock.

Contoh:

Before:

- Display = 24
- On Hand = 76
- Total = 100

Transfer 20:

- Display = 44
- On Hand = 56
- Total = 100

---

## 16. Inventory Movement

Setiap perubahan stock harus dapat ditelusuri.

Movement types:

- PURCHASE_RECEIVING
- SALE
- RETURN
- ADJUSTMENT
- DAMAGE
- EXPIRY
- DISPLAY_TRANSFER
- STOCK_OPNAME

Contoh:

DISPLAY_TRANSFER

- from_location = ON_HAND
- to_location = DISPLAY
- quantity = 20

Inventory Movement menjawab: **Apa yang terjadi pada stock?**

Audit Log menjawab: **Siapa yang melakukan tindakan tersebut, kapan, dan terhadap entity apa?**

---

## 17. Sale & Inventory

Untuk MVP:

- SALE mengurangi Display stock.

Flow:

Customer

↓

Cashier

↓

Sale

↓

Display Quantity - Sale Qty

Jika Display tidak cukup:

Display = 0, On Hand > 0

↓

Warehouse Transfer

↓

Display

Dengan demikian stock tetap konsisten.

---

## 18. Receiving

Default receiving masuk ke:

- ON_HAND

Flow normal:

Warehouse Staff

↓

Input Receiving

↓

PENDING

↓

Warehouse Admin

↓

APPROVE

↓

Inventory + Quantity

↓

Inventory Movement

Saat approval:

- Movement Type = PURCHASE_RECEIVING
- Location = ON_HAND

---

## 19. Receiving Correction

Jika Staff salah input:

PENDING

↓

Admin

- APPROVE
- REJECT
- REQUEST_CORRECTION

REQUEST_CORRECTION lebih disukai daripada Admin mengedit input Staff secara diam-diam. Hal ini menjaga auditability.

---

## 20. Display Transfer

Transfer Display ↔ On Hand:

Warehouse

↓

Select Product

↓

Input Quantity

↓

Transfer

↓

Inventory Movement

Tidak memerlukan approval Admin.

Semua transfer tetap masuk Audit Log.

---

## 21. Stock Opname

Stock Opname merupakan proses terpisah dari Daily Closing.

Stock Opname menghitung:

- Display
- On Hand

secara terpisah.

Flow:

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

Variance tidak otomatis membuat adjustment.

Jika memang diperlukan:

Variance

↓

Investigation

↓

Human Decision

↓

Inventory Adjustment

---

## 22. Warehouse Request

Warehouse dapat meminta barang kepada Owner.

Contoh:

- “Aqua 600ml hampir habis, mohon dilakukan pembelian.”

Flow:

Warehouse Staff/Admin

↓

Warehouse Request

↓

Owner

↓

Review

↓

External Purchasing

AURA tidak melakukan purchasing.

---

## 23. Supplier Management

Supplier hanya dikelola Owner.

Data:

- Supplier
  - id
  - name
  - contact_person
  - phone
  - whatsapp
  - address
  - notes
  - created_at

Relationship:

- Supplier → Supplier Products → Product

Owner dapat:

- create supplier
- edit supplier
- link product
- melihat contact
- membuka WhatsApp

---

## 24. External Purchasing

AURA tidak melakukan order.

Flow:

AI / Analytics

↓

Need Detected

↓

Reorder Recommendation

↓

Owner

↓

Supplier Information

↓

WhatsApp / Contact

↓

External Purchase

↓

Goods Arrive

↓

Warehouse Receiving

Tidak ada:

- AURA → Supplier → Purchase Order

---

## 25. POS

POS ditujukan untuk Windows.

Technology:

- React + Tauri

Flow:

Scan Product

↓

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

---

## 26. Payment

MVP:

- Cash only

Architecture tetap extensible:

- PaymentMethod
  - CashPayment
  - QRISPayment (Future)
  - DebitPayment (Future)
  - CreditPayment (Future)

Tidak ada payment gateway dalam MVP.

---

## 27. Cash Reconciliation

Formula:

Opening Cash

- Cash Sales
- Refunds

± Cash Adjustment

= Expected Cash

Kemudian:

Cash Variance

= Actual Cash - Expected Cash

Contoh:

- Expected = Rp4.750.000
- Actual = Rp4.700.000
- Variance = -Rp50.000

---

## 28. Daily Closing

Daily Closing merupakan satu parent process:

- Daily Closing
  - Cash Closing
  - Inventory Closing

### Cash Closing (Cashier)

Cashier

↓

Submit Cash Closing

↓

Expected Cash

↓

Actual Cash

↓

Variance

Normal cash closing tidak membutuhkan approval Owner.

### Inventory Closing (Warehouse)

Warehouse Staff

↓

Inventory Closing

↓

Warehouse Admin

↓

Review / Finalize

Tidak berarti seluruh SKU harus dihitung.

Daily closing dapat menggunakan:

- selected products
- low-stock products
- high-risk products
- random sampling

Full Stock Opname tetap proses terpisah.

---

## 29. Inventory Closing Formula

Opening Stock

- Receiving
- Sales

± Adjustments

± Returns

± Other Movements

= Expected Closing Stock

Kemudian:

Variance

= Physical Closing Stock - Expected Closing Stock

Karena inventory memiliki Display dan On Hand, physical dihitung terpisah:

- Physical Display
- Physical On Hand

---

## 30. Variance Handling

Variance tidak otomatis menjadi adjustment.

Variance

↓

NEEDS_REVIEW

↓

Human Investigation

↓

Decision

- No Action
- Inventory Adjustment

---

## 31. Audit Log

AURA menggunakan satu centralized audit table.

Actor categories:

- OWNER
- WAREHOUSE_ADMIN
- WAREHOUSE_STAFF
- CASHIER
- AI

Schema:

- audit_logs
  - id
  - actor_id
  - actor_type
  - action
  - entity_type
  - entity_id
  - before_data
  - after_data
  - metadata
  - timestamp
  - ip/device/session

---

## 32. Audit Events

Contoh event:

- Authentication
  - LOGIN
  - LOGOUT
  - LOGIN_FAILED
- Product
  - PRODUCT_REGISTRATION_SUBMITTED
  - PRODUCT_APPROVED
  - PRODUCT_REJECTED
  - PRODUCT_UPDATED
  - PRODUCT_DEACTIVATED
- Receiving
  - RECEIVING_SUBMITTED
  - RECEIVING_APPROVED
  - RECEIVING_REJECTED
  - RECEIVING_CORRECTION_REQUESTED
- Inventory
  - DISPLAY_TRANSFER
  - INVENTORY_ADJUSTMENT
  - STOCK_OPNAME_SUBMITTED
  - STOCK_OPNAME_APPROVED
- Sales
  - SALE_CREATED
  - SALE_VOIDED
  - REFUND_CREATED
  - DISCOUNT_APPLIED
- Closing
  - CASH_CLOSING_SUBMITTED
  - INVENTORY_CLOSING_SUBMITTED
  - CLOSING_REVIEWED
  - CLOSING_FINALIZED
- Warehouse
  - WAREHOUSE_REQUEST_CREATED
  - WAREHOUSE_REQUEST_UPDATED
  - WAREHOUSE_REQUEST_RESOLVED
- Supplier
  - SUPPLIER_CREATED
  - SUPPLIER_UPDATED
  - SUPPLIER_PRODUCT_LINKED
- AI
  - AI_INVESTIGATION
  - AI_INSIGHT_GENERATED
  - AI_RECOMMENDATION_GENERATED

---

## 33. Audit Immutability

Audit log tidak boleh diubah atau dihapus oleh user.

Jika ada koreksi:

Old Event

↓

New Corrective Event

bukan:

- UPDATE old audit record

---

## 34. AI Architecture

AI AURA terdiri dari:

- AI Services
  - Demand Forecast
  - Stockout Risk
  - Anomaly Detection
  - Event Intelligence
  - Recommendation
- Hermes
  - Reasoning
  - Tool Calling
  - Investigation
  - Explanation
  - Conversation

---

## 35. AI Priority

Tier 1:

- Demand Forecast
- Stockout Risk
- Event Intelligence
- Reorder Recommendation

Tier 2:

- Sales Anomaly
- Inventory Anomaly

Tier 3:

- Promotion Recommendation
- Dead Stock
- Advanced Business Insight

---

## 36. Hermes

Hermes adalah conversational reasoning/orchestration layer.

Contoh:

“Kenapa penjualan Aqua turun minggu ini?”

Hermes:

Question

↓

Understand intent

↓

MCP tools

↓

Sales data

↓

Inventory data

↓

Event context

↓

Analysis

↓

Evidence

↓

Explanation

---

## 37. AI Investigation

Hermes dapat menginvestigasi variance dari:

- Daily Closing
- Inventory Movement
- Sales
- Receiving
- Stock Opname
- Cash Closing
- Audit Log

Kemudian menghasilkan:

- Finding
- Evidence
- Possible Cause
- Confidence
- Recommendation

Confidence:

- HIGH
- MEDIUM
- LOW
- UNKNOWN

Jika evidence tidak cukup:

- “Cause could not be determined from available data.”

AI tidak boleh mengarang penyebab. AI juga tidak boleh menyatakan fraud tanpa evidence.

---

## 38. AI Permission Model

Prinsip:

- Hermes mewarisi authorization context dari current user.

Artinya:

- Owner → Hermes → MCP → Owner permissions
- Cashier → Hermes → MCP → Cashier permissions

AI tidak mendapatkan privilege tambahan.

AI capability ≠ User permission

---

## 39. MCP Architecture

MCP berada di backend yang sama.

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

Tidak boleh:

- Hermes → PostgreSQL

---

## 40. MCP Tool Categories

### READ

- get_sales_summary()
- get_sales_history()
- get_product()
- get_products()
- get_inventory()
- get_inventory_movements()
- get_receivings()
- get_supplier()
- get_supplier_products()
- get_upcoming_events()
- get_weather_context()
- get_audit_logs()
- get_entity_history()
- get_daily_closing()

### ANALYZE

- forecast_demand()
- calculate_stockout_risk()
- detect_sales_anomalies()
- detect_inventory_anomalies()
- analyze_event_impact()
- analyze_closing_variance()
- analyze_inventory_variance()
- analyze_cash_variance()

### RECOMMEND

- generate_reorder_recommendation()
- generate_business_insight()
- generate_inventory_action()
- generate_supplier_contact_recommendation()

Tidak ada critical mutation tool.

---

## 41. AI Restrictions

Hermes tidak boleh:

- create product
- update product
- delete product
- receive inventory
- adjust inventory
- create sale
- change price
- approve receiving
- approve product
- approve stock opname
- execute purchasing
- create PO
- modify audit log

AI boleh:

- read
- analyze
- forecast
- correlate
- explain
- recommend
- generate insight
- generate notification

---

## 42. AI Notification

AI bukan Notification Service.

AI

↓

Detect Risk

↓

AI Insight

↓

Notification Service

↓

Owner

Contoh:

- “Aqua 600ml memiliki risiko stockout tinggi dalam 4 hari.”

---

## 43. Event Intelligence

AURA menggunakan abstraction:

Context Provider

- Calendar Provider
- Weather Provider
- Event Provider
- Trend Provider

↓

Context Engine

↓

Normalized Signals

↓

AI

MVP:

- Calendar / holiday
- Weather
- Satu external event/trend source

Future:

- school holiday
- concert
- sport event
- local event
- traffic
- regional trends

Event-specific business rules tidak di-hardcode ke core AI.

---

## 44. Event → Demand

AURA harus mencoba menghubungkan context dengan demand.

Contoh:

Heavy Rain

- Historical Rainy-Day Sales

↓ Demand Signal

↓ Forecast

↓ Stockout Risk

↓ Recommendation

Atau:

Local Event

- Historical Event Pattern

↓ Demand Impact

---

## 45. Recommendation Engine

Recommendation harus berbasis evidence.

Contoh:

Product: Aqua 600ml

Current: Display = 12, On Hand = 8, Total = 20

Forecast: Daily Demand = 8/day

Risk: Stockout ≈ 2–3 days

Supplier: Supplier A

Recommendation:

- Contact Supplier A for replenishment.

AI menjelaskan mengapa rekomendasi diberikan.

---

## 46. Frontend Architecture

AURA frontend terdiri dari:

- aura-frontend
  - apps/
    - web/
    - mobile/
    - pos/
  - packages/
    - ui/
    - api-client/
    - types/
    - validation/
    - config/

---

## 47. Expo Web

Expo Web digunakan untuk:

### Owner

- Dashboard
- Sales Analytics
- Inventory Intelligence
- AI Attention
- AI Recommendations
- Events
- Suppliers
- Warehouse Requests
- Hermes
- Audit Logs
- Settings

### Warehouse (Admin/Staff)

- Dashboard
- Inventory
- Receiving
- Product Requests
- Products
- Stock Movement
- Stock Opname
- Daily Closing
- Warehouse Requests
- AI Insights

---

## 48. Expo Mobile

Expo Mobile terutama disiapkan untuk warehouse.

Target capability:

- Scan EAN-13
- Receiving
- Inventory lookup
- Stock checking
- Stock opname
- Warehouse request

Mobile dapat menggunakan kamera sebagai barcode scanner.

---

## 49. Tauri POS

Windows POS:

Windows

↓

Tauri

↓

React

↓

POS

Interface harus optimized untuk:

- keyboard
- barcode scanner
- fast product lookup
- rapid cart operation
- cash payment

---

## 50. Frontend State

Zustand untuk client/UI state:

- auth
- cart
- ui
- notification
- temporary POS state

TanStack Query untuk server state:

- Products
- Inventory
- Sales
- Analytics
- AI Insights
- Suppliers
- Warehouse Requests

---

## 51. API Client

Shared frontend package:

- packages/api-client/
  - auth
  - products
  - inventory
  - sales
  - warehouse
  - analytics
  - suppliers
  - ai

---

## 52. API Contract

Backend menjadi source of truth.

FastAPI

↓ OpenAPI

↓ Generated TypeScript API Client / Types

↓ Frontend

Frontend dan backend tidak berbagi source code type secara langsung.

---

## 53. Frontend Validation

Frontend:

- Zod

Backend:

- Pydantic

Flow:

Frontend

↓ Zod

↓ API

↓ Pydantic

↓ Application Service

Backend tetap menjadi security boundary.

---

## 54. Backend Architecture

Backend adalah Modular Monolith.

- aura-backend/
  - app/
    - modules/
    - mcp/
    - core/
    - infrastructure/
  - tests/
  - alembic/
  - Dockerfile
  - pyproject.toml

---

## 55. Backend Modules

- modules/
  - auth/
  - users/
  - products/
  - inventory/
  - sales/
  - warehouse/
  - suppliers/
  - analytics/
  - events/
  - ai/
  - notifications/
  - audit/

---

## 56. Module Internal Structure

Setiap domain module menggunakan:

- module/
  - api/
  - application/
  - domain/
  - infrastructure/

Contoh:

- inventory/
  - api/
    - inventory_router.py
  - application/
    - transfer_display.py
    - adjust_inventory.py
    - stock_opname.py
  - domain/
    - inventory.py
    - movement.py
    - exceptions.py
  - infrastructure/
    - inventory_repository.py
    - models.py

---

## 57. Backend Layer

API

↓

Application / Use Case

↓

Domain

↓

Infrastructure

↓

Database / External Service

Business rules berada di Domain/Application layer (bukan di Hermes).

---

## 58. Technology Stack

### Frontend

| Component       | Technology     |
| --------------- | -------------- |
| Language        | TypeScript     |
| UI              | React          |
| Web/Mobile      | Expo           |
| Desktop         | Tauri          |
| State           | Zustand        |
| Server state    | TanStack Query |
| Validation      | Zod            |
| Package manager | pnpm           |

### Backend

| Component        | Technology |
| ---------------- | ---------- |
| Language         | Python     |
| API              | FastAPI    |
| Validation       | Pydantic   |
| ORM              | SQLAlchemy |
| Migration        | Alembic    |
| Database         | PostgreSQL |
| Auth             | JWT        |
| Password hashing | Argon2id   |
| Testing          | Pytest     |

### AI

| Component     | Technology                    |
| ------------- | ----------------------------- |
| LLM           | External LLM API              |
| Orchestration | Hermes                        |
| Tool protocol | MCP                           |
| Forecasting   | Internal AI service           |
| Analytics     | Internal AI/Business services |

### Infrastructure

| Component  | Technology       |
| ---------- | ---------------- |
| Container  | Docker           |
| Deployment | Dokploy          |
| Server     | VPS              |
| Database   | PostgreSQL       |
| HTTPS      | Reverse proxy    |
| Cache      | Redis (optional) |

---

## 59. Repository Architecture

AURA menggunakan dua repository:

- aura-frontend
- aura-backend

---

## 60. Database

Primary database:

- PostgreSQL

Core tables:

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

---

## 61. Core Relationships (ringkas)

- Product
  - Inventory
  - Inventory Movements
  - Sale Items
  - Receiving Items
  - Supplier Products
  - Stock Opname
- Supplier
  - Supplier Products
  - Product
- Daily Closing
  - Cash Closing
  - Inventory Closing

---

## 62. Deployment Architecture

Semua server-side deployment melalui Dokploy.

INTERNET

↓

Dokploy (Reverse Proxy)

↓

- Expo Web
- AURA Backend
  - PostgreSQL
  - External LLM
  - External APIs

MCP tidak menjadi container/service terpisah — MCP berada dalam AURA Backend.

---

## 63. POS Deployment

Tauri bukan deployment server.

aura-frontend

↓ Tauri Build

↓ AURA POS.exe

↓ Windows Cashier

↓ HTTPS

↓ AURA Backend

---

## 64. Redis

Redis bersifat optional.

Tidak boleh menjadi dependency wajib untuk core business operation.

Jika digunakan:

- caching
- temporary state
- rate limiting
- future queue/background jobs

Database PostgreSQL tetap menjadi source of truth.

---

## 65. Reliability

MVP menggunakan online-first architecture.

POS

↓ Internet

Backend

↓

PostgreSQL

Tidak ada offline-first synchronization pada MVP.

Namun architecture tidak boleh menutup kemungkinan future (sinkronisasi offline-first).

---

## 66. Security Principles

- Backend sebagai security boundary
- AI isolation (LLM tidak memiliki DB credentials)
- MCP isolation (MCP hanya dapat menggunakan registered tools)
- Auditability (critical mutation harus dapat dilacak)
- Least privilege
- AI non-authority (AI tidak memiliki authority untuk melakukan critical business mutation)

---

## 67. AI Data Access

LLM tidak diberikan raw database access.

LLM

↓ Hermes

↓ MCP

↓ Application Service

↓ Repository

↓ Database

AI menerima data terstruktur yang dibutuhkan untuk reasoning.

---

## 68. Analytics (minimum)

### Sales

- Revenue
- Units sold
- Sales by product
- Sales by category
- Sales trend
- Daily/weekly comparison

### Inventory

- Current stock
- Low stock
- Stock movement
- Stock turnover
- Stockout risk

### Business

- Best sellers
- Slow movers
- Demand trend
- Event impact

---

## 69. AI Dashboard

Owner memiliki area: **AI Attention**.

Contoh:

- HIGH — Aqua 600ml berisiko stockout dalam 3 hari.
- MEDIUM — Penjualan snack meningkat 22% menjelang event lokal.
- LOW — 5 produk memiliki inventory turnover rendah.

Setiap insight harus dapat dibuka untuk melihat evidence.

---

## 70. Recommendation UI (contoh)

Stockout Risk — Aqua 600ml

- Risk: HIGH
- Estimated stockout: 3 days
- Current stock: 20
- Avg demand: 8/day

Recommendation:

- Contact Supplier A for replenishment.

AURA tidak melakukan order.

---

## 71. Hermes UI

Owner dapat berbicara dengan Hermes.

Contoh prompt:

- “Apa yang harus saya perhatikan hari ini?”

Hermes menggabungkan:

- sales
- inventory
- forecast
- events
- anomaly
- closing
- warehouse requests

dan menghasilkan prioritized attention list.

---

## 72. Example Hermes Investigation

User:

- “Kenapa stok Aqua kurang 3?”

Hermes:

1. Read current inventory
2. Read expected inventory
3. Read inventory movements
4. Read sales
5. Read receiving
6. Read audit logs
7. Correlate timeline
8. Produce finding

Output:

- Finding: Terdapat variance 3 unit.
- Evidence: expected vs physical, timeline movement, dsb.
- Possible cause (tanpa mengarang)
- Confidence: MEDIUM
- Recommendation: physical verification + review transfer (tidak langsung adjustment)

---

## 73. Notifications

Notification types:

- AI_INSIGHT
- STOCKOUT_RISK
- LOW_STOCK
- ANOMALY
- WAREHOUSE_REQUEST
- CLOSING_VARIANCE
- PRODUCT_REQUEST
- RECEIVING_PENDING

Recipient ditentukan berdasarkan role dan scope.

---

## 74. Frontend Screen Map

### Owner

- Dashboard
- Sales Analytics
- Inventory Intelligence
- AI Attention
- AI Recommendations
- Events
- Suppliers
- Warehouse Requests
- Hermes
- Audit Logs
- Settings

### Warehouse Admin

- Dashboard
- Inventory
- Products
- Product Requests
- Receiving
- Stock Movement
- Stock Opname
- Inventory Closing
- Warehouse Requests
- AI Insights

### Warehouse Staff

- Inventory
- Scan
- Receiving
- Product Requests
- Stock Opname
- Warehouse Requests
- AI Insights

### Cashier

- POS
- Transaction History
- Cash Closing

---

## 75. API Architecture (grouping contoh)

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

Exact endpoint naming dapat disesuaikan saat implementation.

---

## 76. Testing Strategy

Testing dibagi:

- unit
- integration
- e2e

### Unit (contoh)

- inventory calculation
- display transfer
- stockout calculation
- closing calculation
- permission policy
- recommendation logic

### Integration (contoh)

- database
- API
- receiving
- sales
- closing
- audit

### E2E

Critical user journeys.

---

## 77. Critical E2E Flows (minimal)

1. Login → Dashboard
2. Scan Unknown Product → Product Request → Admin Approve → Product Created
3. Receiving → Admin Approval → Inventory Increased
4. Display Transfer → Inventory Movement → Audit Log
5. POS → Scan → Cart → Cash → Sale → Inventory Reduction
6. Cash Closing → Variance
7. Inventory Closing → Variance → AI Investigation
8. Stock Opname → Variance → Admin Approval → Optional Adjustment
9. AI → Stockout Detection → Recommendation → Owner → Supplier Contact

---

## 78. Acceptance Principles

AURA MVP dianggap berhasil jika:

### Operational Integrity

- setiap sale tercatat,
- inventory berubah sesuai business rules,
- receiving dapat ditelusuri,
- display dan on-hand selalu konsisten,
- critical mutation memiliki audit trail.

### Human Control

- AI tidak dapat melakukan critical mutation,
- approval tetap dilakukan manusia,
- purchasing tetap dilakukan Owner secara eksternal.

### AI Intelligence

- AI dapat membaca operational context,
- AI dapat forecast,
- AI dapat mendeteksi anomaly,
- AI dapat memberikan recommendation,
- AI dapat menjelaskan evidence.

### User Experience

- Cashier dapat melakukan transaksi dengan cepat,
- Warehouse dapat menerima barang dengan workflow jelas,
- Owner mendapatkan actionable insight tanpa harus membaca semua data manual.

---

## 79. Implementation Roadmap

Urutan implementasi yang disarankan:

1. PHASE 0 — Domain & Architecture
2. PHASE 1 — Repository & Backend Foundation
3. PHASE 2 — Database & Migration
4. PHASE 3 — Authentication + RBAC
5. PHASE 4 — Product Master
6. PHASE 5 — Inventory
7. PHASE 6 — Warehouse Workflow
8. PHASE 7 — POS + Sales
9. PHASE 8 — Daily Closing
10. PHASE 9 — Audit Log
11. PHASE 10 — Analytics
12. PHASE 11 — AI Services
13. PHASE 12 — MCP + Hermes
14. PHASE 13 — Event Intelligence
15. PHASE 14 — Notifications
16. PHASE 15 — Integration / E2E Testing
17. PHASE 16 — Docker
18. PHASE 17 — Dokploy
19. PHASE 18 — Demo Hardening

---

## 80. Recommended Development Priority (Hackathon)

Untuk hackathon, jangan mencoba menyelesaikan semua AI sekaligus.

Prioritas:

- Operational system (POS + Inventory + Warehouse + Closing + Audit) harus stabil terlebih dahulu,
- lalu Intelligence (Forecast + Stockout + Recommendation + Hermes).

---

## 81. Hackathon Demo Story

Demo terbaik AURA bukan sekadar: “Ini dashboard AI kami.”

Tetapi menunjukkan satu cerita end-to-end:

1. **Operation** — Warehouse menerima produk (scan → receiving → inventory updated)
2. **Sales** — Cashier menjual produk (scan → cash → sale → inventory decreases)
3. **Intelligence** — AURA mengamati sales + inventory + weather/event
4. **Prediction** — “Aqua berisiko stockout dalam 3 hari.”
5. **Recommendation** — “Hubungi Supplier A untuk replenishment.”
6. **Human Decision** — Owner membuka supplier (Contact/WhatsApp) dan membeli di luar AURA
7. **Investigation** — Owner bertanya “Kenapa stok Aqua kurang 3?” → Hermes investigasi + evidence + confidence

Ini memperlihatkan filosofi:

Observe → Understand → Predict → Recommend → Human Decision → Real-world Action

---

## 82. Final Architecture (ringkas)

Users:

- Owner
- Warehouse Admin
- Warehouse Staff
- Cashier

Clients:

- Expo Web
- Expo Mobile
- Tauri POS

Backend:

- AURA Backend (Modular Monolith, FastAPI)
  - Business Modules (Products, Inventory, Sales, Warehouse, Suppliers, Closing, Audit)
  - AI Services (Forecast, Anomaly, Recommendation, Event)
  - MCP Gateway / Tools
- PostgreSQL
- External LLM API

---

## 83. Final Architectural Principles

AURA v2 memiliki prinsip yang tidak boleh dilanggar selama development:

1. Human remains in control — AI recommends, human decides, human acts
2. AI never bypasses backend — Hermes → MCP → Application Service → DB
3. No critical mutation through AI (Purchase/Approve/Adjust/Create Sale/Change Product)
4. Inventory has one source of truth (Display + On Hand)
5. Total Available is derived (Total = Display + On Hand)
6. Audit is immutable (Correction = New Event)
7. Purchasing remains external (AURA recommends, owner acts externally)
8. Backend owns business rules (bukan frontend, bukan Hermes)
9. Single-store MVP (no multi-tenant complexity)
10. Modular, not microservices (Modular Monolith untuk MVP, dengan boundary yang bisa diekstrak di masa depan)

---

## 84. Definition of Done — AURA POS v2 MVP

AURA MVP siap untuk demo ketika seluruh flow utama berikut dapat berjalan:

- Warehouse scan/receiving → inventory updated
- POS sale → inventory decreases
- Operational data → analytics/AI → forecast/risk
- Recommendation → owner action externally

Dengan PRD ini, AURA POS v2 sudah cukup lengkap untuk menjadi baseline implementation. Seluruh keputusan besar yang dibahas sudah dikonsolidasikan: dua repository (aura-frontend dan aura-backend), Expo Web + Expo Mobile + Tauri, MCP di dalam backend yang sama, external LLM, serta lifecycle Product ACTIVE / INACTIVE / ARCHIVED.
