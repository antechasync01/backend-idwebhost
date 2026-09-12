import pytest
from unittest.mock import MagicMock
from app.modules.users.infrastructure.models import UserRole
from app.mcp.gateway import MCPContextGateway
from app.core.exceptions import ForbiddenError


def test_mcp_gateway_rbac_allowed():
    mock_user = MagicMock()
    mock_user.role = UserRole.OWNER
    mock_db = MagicMock()

    tools = MCPContextGateway.list_tools(mock_user)
    tool_names = [t["name"] for t in tools]

    assert "get_inventory_stock" in tool_names
    assert "get_stockout_risk_products" in tool_names
    assert "get_sales_summary" in tool_names
    assert "analyze_sales_anomalies" in tool_names
    assert "generate_reorder_recommendations" in tool_names


def test_mcp_gateway_rbac_forbidden():
    mock_user = MagicMock()
    mock_user.role = UserRole.CASHIER
    mock_db = MagicMock()

    with pytest.raises(ForbiddenError):
        MCPContextGateway.execute_tool("get_stockout_risk_products", {}, mock_db, mock_user)


def test_get_top_selling_products_queries_gtin():
    from app.mcp.tools.read.sales_tools import get_top_selling_products

    mock_db = MagicMock()
    mock_db.execute.return_value.all.return_value = [
        ("uuid-123", "8881234567890", "Kopi Susu", 15, 300000.0)
    ]

    result = get_top_selling_products(mock_db, limit=5)
    assert len(result) == 1
    assert result[0]["gtin"] == "8881234567890"
    assert result[0]["name"] == "Kopi Susu"


def test_get_inventory_stock_queries_gtin():
    from app.mcp.tools.read.inventory_tools import get_inventory_stock

    mock_db = MagicMock()
    mock_inv = MagicMock(display_quantity=10, on_hand_quantity=50)
    mock_prod = MagicMock(id="prod-uuid", gtin="8881234567890", name="Teh Botol")
    del mock_prod.minimum_stock_alert  # simulate no attribute on Product model
    mock_cat = MagicMock(name="Minuman")

    mock_db.execute.return_value.all.return_value = [(mock_inv, mock_prod, mock_cat)]

    result = get_inventory_stock(mock_db)
    assert len(result) == 1
    assert result[0]["gtin"] == "8881234567890"
    assert result[0]["total_quantity"] == 60
    assert result[0]["minimum_stock_alert"] == 10


def test_analyze_sales_anomalies():
    from app.mcp.tools.analyze.anomaly_tools import analyze_sales_anomalies

    mock_db = MagicMock()
    mock_inv = MagicMock(display_quantity=0, on_hand_quantity=20)
    mock_prod = MagicMock(id="prod-uuid-1", gtin="8881112223334", name="Susu UHT")
    mock_db.execute.return_value.all.side_effect = [
        [(mock_inv, mock_prod)],  # inventories query
        []  # sales query
    ]

    results = analyze_sales_anomalies(mock_db)
    assert len(results) == 1
    assert results[0]["anomaly_type"] == "UNSHELVED_STOCK"
    assert results[0]["gtin"] == "8881112223334"


def test_generate_reorder_recommendations():
    from app.mcp.tools.recommend.reorder_tools import generate_reorder_recommendations

    mock_db = MagicMock()
    mock_inv = MagicMock(display_quantity=2, on_hand_quantity=3)
    mock_prod = MagicMock(id="prod-uuid-2", gtin="8885556667778", name="Minyak Goreng 2L")
    del mock_prod.minimum_stock_alert  # fallback to 10

    mock_supplier = MagicMock()
    mock_supplier.name = "PT Distribusi Jaya"
    mock_sp = MagicMock()

    mock_db.execute.return_value.all.side_effect = [
        [(mock_inv, mock_prod)],  # inventories
        []  # sales
    ]
    mock_db.execute.return_value.first.return_value = (mock_sp, mock_supplier)

    results = generate_reorder_recommendations(mock_db)
    assert len(results) == 1
    assert results[0]["gtin"] == "8885556667778"
    assert results[0]["primary_supplier"] == "PT Distribusi Jaya"
    assert results[0]["recommended_reorder_qty"] >= 24


def test_mcp_server_module_loads():
    from app.mcp.server import mcp, get_system_owner_user
    assert mcp.name == "aura-pos-mcp-server"
    user = get_system_owner_user()
    assert user.role == UserRole.OWNER
    assert user.full_name == "Hermes Agent Context"

