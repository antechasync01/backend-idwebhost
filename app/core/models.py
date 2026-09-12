"""Central ORM Model Registry for AURA POS Backend.

Importing this module ensures all SQLAlchemy models are registered in Base.metadata.
"""

from app.core.database import Base
from app.modules.users.infrastructure.models import (
    User,
    UserRole,
    Role,
    Permission,
    RolePermission,
)
from app.modules.products.infrastructure.models import (
    Category,
    Product,
    ProductStatus,
    ProductRegistrationRequest,
    RegistrationStatus,
)
from app.modules.inventory.infrastructure.models import (
    Inventory,
    InventoryMovement,
    MovementType,
    StockOpname,
    StockOpnameStatus,
    StockOpnameItem,
    StockOpnameItemStatus,
)
from app.modules.suppliers.infrastructure.models import (
    Supplier,
    SupplierProduct,
)
from app.modules.warehouse.infrastructure.models import (
    Receiving,
    ReceivingStatus,
    ReceivingItem,
    WarehouseRequest,
    WarehouseRequestStatus,
)
from app.modules.sales.infrastructure.models import (
    Sale,
    SaleItem,
    SaleRefund,
    SaleRefundItem,
    SaleStatus,
    PaymentMethod,
    DailyClosing,
    DailyClosingStatus,
    CashClosing,
    InventoryClosing,
    InventoryClosingItem,
    InventoryClosingVarianceStatus,
)
from app.modules.audit.infrastructure.models import AuditLog, ActorType
from app.modules.events.infrastructure.models import ExternalEvent, EventImpactLevel
from app.modules.ai.infrastructure.models import (
    AIInsight,
    InsightType,
    InsightPriority,
    InsightStatus,
    InsightCategory,
    InsightSeverity,
    StockoutRiskScore,
    DemandForecast,
    RiskLevel,
)
from app.modules.notifications.infrastructure.models import Notification, NotificationType

__all__ = [
    "Base",
    "User",
    "UserRole",
    "Role",
    "Permission",
    "RolePermission",
    "Category",
    "Product",
    "ProductStatus",
    "ProductRegistrationRequest",
    "RegistrationStatus",
    "Inventory",
    "InventoryMovement",
    "MovementType",
    "StockOpname",
    "StockOpnameStatus",
    "StockOpnameItem",
    "StockOpnameItemStatus",
    "Supplier",
    "SupplierProduct",
    "Receiving",
    "ReceivingStatus",
    "ReceivingItem",
    "WarehouseRequest",
    "WarehouseRequestStatus",
    "Sale",
    "SaleItem",
    "SaleRefund",
    "SaleRefundItem",
    "SaleStatus",
    "PaymentMethod",
    "DailyClosing",
    "DailyClosingStatus",
    "CashClosing",
    "InventoryClosing",
    "InventoryClosingItem",
    "InventoryClosingVarianceStatus",
    "AuditLog",
    "ActorType",
    "ExternalEvent",
    "EventImpactLevel",
    "AIInsight",
    "InsightType",
    "InsightPriority",
    "InsightStatus",
    "InsightCategory",
    "InsightSeverity",
    "StockoutRiskScore",
    "DemandForecast",
    "RiskLevel",
    "Notification",
    "NotificationType",
]
