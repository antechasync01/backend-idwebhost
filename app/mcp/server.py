"""AURA POS MCP Server — Official Model Context Protocol Server for Hermes Agent.

Run via Stdio (Default for Hermes Agent CLI / Claude Desktop / IDEs):
    uv run python -m app.mcp.server

Run via Streamable HTTP (Default for Hermes Agent Docker/SSE):
    uv run python -m app.mcp.server --transport sse

Run via Streamable HTTP:
    uv run python -m app.mcp.server --transport streamable-http
"""

import sys
from typing import Any
from mcp.server import MCPServer
from app.core.database import SessionLocal
from app.modules.users.infrastructure.models import User, UserRole
from app.mcp.gateway import MCPContextGateway

# Initialize MCPServer (v2 API)
mcp = MCPServer("aura-pos-mcp-server")


def get_system_owner_user() -> User:
    """Return default Owner security context for Hermes Agent MCP execution."""
    user = User()
    user.role = UserRole.OWNER
    user.full_name = "Hermes Agent Context"
    return user


@mcp.tool()
def get_inventory_stock(product_id: str | None = None, category_id: str | None = None) -> list[dict[str, Any]]:
    """Ambil data stok produk (Display stock & On-Hand stock) di minimarket AURA POS."""
    db = SessionLocal()
    try:
        user = get_system_owner_user()
        args = {}
        if product_id:
            args["product_id"] = product_id
        if category_id:
            args["category_id"] = category_id
        return MCPContextGateway.execute_tool("get_inventory_stock", args, db, user)
    finally:
        db.close()


@mcp.tool()
def get_stockout_risk_products(threshold_days: float = 7.0) -> list[dict[str, Any]]:
    """Ambil daftar produk yang berisiko habis dalam N hari berdasarkan burn-rate penjualan."""
    db = SessionLocal()
    try:
        user = get_system_owner_user()
        return MCPContextGateway.execute_tool("get_stockout_risk_products", {"threshold_days": threshold_days}, db, user)
    finally:
        db.close()


@mcp.tool()
def get_sales_summary(start_date: str | None = None, end_date: str | None = None) -> dict[str, Any]:
    """Ambil ringkasan performa penjualan (total omzet, jumlah transaksi, rata-rata keranjang)."""
    db = SessionLocal()
    try:
        user = get_system_owner_user()
        args = {}
        if start_date:
            args["start_date"] = start_date
        if end_date:
            args["end_date"] = end_date
        return MCPContextGateway.execute_tool("get_sales_summary", args, db, user)
    finally:
        db.close()


@mcp.tool()
def get_top_selling_products(limit: int = 5) -> list[dict[str, Any]]:
    """Ambil daftar N produk paling laris terjual."""
    db = SessionLocal()
    try:
        user = get_system_owner_user()
        return MCPContextGateway.execute_tool("get_top_selling_products", {"limit": limit}, db, user)
    finally:
        db.close()


@mcp.tool()
def analyze_sales_anomalies() -> list[dict[str, Any]]:
    """Analisis anomali stok dan penjualan (dead stock, barang belum dipajang di display)."""
    db = SessionLocal()
    try:
        user = get_system_owner_user()
        return MCPContextGateway.execute_tool("analyze_sales_anomalies", {}, db, user)
    finally:
        db.close()


@mcp.tool()
def generate_reorder_recommendations(product_id: str | None = None) -> list[dict[str, Any]]:
    """Hasilkan rekomendasi reorder/pengadaan produk ke supplier berdasarkan burn-rate dan batas stok minimum."""
    db = SessionLocal()
    try:
        user = get_system_owner_user()
        args = {}
        if product_id:
            args["product_id"] = product_id
        return MCPContextGateway.execute_tool("generate_reorder_recommendations", args, db, user)
    finally:
        db.close()


@mcp.tool()
def get_upcoming_events(days: int = 7) -> list[dict[str, Any]]:
    """Ambil daftar event/acara yang akan datang dalam N hari ke depan dari Google Calendar (hari libur, promo, dll)."""
    from app.modules.events.application.events_service import EventsService
    db = SessionLocal()
    try:
        service = EventsService(db)
        return service.get_upcoming_events(days=days)
    finally:
        db.close()


# Expose Starlette ASGI Application for SSE Transport (backwards compat)
sse_app = mcp.sse_app(sse_path="/sse", host="0.0.0.0")

if __name__ == "__main__":
    transport = "stdio"
    if "--transport" in sys.argv:
        idx = sys.argv.index("--transport")
        if idx + 1 < len(sys.argv):
            transport = sys.argv[idx + 1]

    if transport == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=8001)
    elif transport == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
    else:
        mcp.run(transport="stdio")
