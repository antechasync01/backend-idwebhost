from typing import Callable, Any
from app.modules.users.infrastructure.models import UserRole
from app.mcp.tools.read.inventory_tools import get_inventory_stock, get_stockout_risk_products
from app.mcp.tools.read.sales_tools import get_sales_summary, get_top_selling_products
from app.mcp.tools.analyze.anomaly_tools import analyze_sales_anomalies
from app.mcp.tools.recommend.reorder_tools import generate_reorder_recommendations


class MCPToolDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        allowed_roles: list[UserRole],
        func: Callable[..., Any],
        parameters: dict[str, Any]
    ):
        self.name = name
        self.description = description
        self.allowed_roles = allowed_roles
        self.func = func
        self.parameters = parameters


TOOL_REGISTRY: dict[str, MCPToolDefinition] = {
    # Read Tools
    "get_inventory_stock": MCPToolDefinition(
        name="get_inventory_stock",
        description="Ambil data stok produk (Display stock & On-Hand stock) di minimarket.",
        allowed_roles=[UserRole.OWNER, UserRole.WAREHOUSE_ADMIN, UserRole.WAREHOUSE_STAFF],
        func=get_inventory_stock,
        parameters={
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "Optional UUID produk"},
                "category_id": {"type": "string", "description": "Optional UUID kategori produk"}
            }
        }
    ),
    "get_stockout_risk_products": MCPToolDefinition(
        name="get_stockout_risk_products",
        description="Ambil daftar produk yang berisiko habis dalam X hari berdasarkan burn rate penjualan.",
        allowed_roles=[UserRole.OWNER, UserRole.WAREHOUSE_ADMIN],
        func=get_stockout_risk_products,
        parameters={
            "type": "object",
            "properties": {
                "threshold_days": {"type": "number", "default": 7.0, "description": "Batas hari risiko kehabisan stok"}
            }
        }
    ),
    "get_sales_summary": MCPToolDefinition(
        name="get_sales_summary",
        description="Ambil ringkasan performa penjualan (total omzet, jumlah transaksi, rata-rata keranjang).",
        allowed_roles=[UserRole.OWNER, UserRole.WAREHOUSE_ADMIN],
        func=get_sales_summary,
        parameters={
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Tanggal mulai (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "Tanggal selesai (YYYY-MM-DD)"}
            }
        }
    ),
    "get_top_selling_products": MCPToolDefinition(
        name="get_top_selling_products",
        description="Ambil daftar N produk paling laris terjual.",
        allowed_roles=[UserRole.OWNER, UserRole.WAREHOUSE_ADMIN],
        func=get_top_selling_products,
        parameters={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 5, "description": "Jumlah produk teratas"}
            }
        }
    ),

    # Analyze Tools
    "analyze_sales_anomalies": MCPToolDefinition(
        name="analyze_sales_anomalies",
        description="Analisis anomali stok dan penjualan (dead stock, barang belum dipajang di display).",
        allowed_roles=[UserRole.OWNER, UserRole.WAREHOUSE_ADMIN],
        func=analyze_sales_anomalies,
        parameters={
            "type": "object",
            "properties": {}
        }
    ),

    # Recommend Tools
    "generate_reorder_recommendations": MCPToolDefinition(
        name="generate_reorder_recommendations",
        description="Hasilkan rekomendasi reorder/pengadaan produk ke supplier berdasarkan burn-rate dan batas stok minimum.",
        allowed_roles=[UserRole.OWNER, UserRole.WAREHOUSE_ADMIN],
        func=generate_reorder_recommendations,
        parameters={
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "Optional UUID produk spesifik"}
            }
        }
    )
}


def get_available_tools_for_role(role: UserRole | str | None) -> list[dict[str, Any]]:
    """Return tool schemas available for a specific user role."""
    if not role:
        return []

    target_role: UserRole | None = None
    if isinstance(role, UserRole):
        target_role = role
    elif isinstance(role, str):
        try:
            target_role = UserRole(role)
        except ValueError:
            return []

    available = []
    for tool in TOOL_REGISTRY.values():
        if target_role in tool.allowed_roles:
            available.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            })
    return available
