from typing import Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.inventory.infrastructure.models import Inventory
from app.modules.products.infrastructure.models import Product
from app.modules.sales.infrastructure.models import SaleItem, Sale, SaleStatus
from app.modules.ai.infrastructure.models import StockoutRiskScore, RiskLevel


def calculate_stockout_risks(db: Session) -> list[dict[str, Any]]:
    """Calculate and return stockout risk scores for all products in inventory."""
    inventories = db.execute(
        select(Inventory, Product).join(Product, Inventory.product_id == Product.id)
    ).all()

    # Get recent sales quantity per product
    sales_stmt = (
        select(
            SaleItem.product_id,
            func.sum(SaleItem.quantity).label("total_sold")
        )
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.status == SaleStatus.COMPLETED)
        .group_by(SaleItem.product_id)
    )
    sales_map = {row.product_id: float(row.total_sold or 0) for row in db.execute(sales_stmt).all()}

    risks = []
    for inv, prod in inventories:
        total_stock = inv.display_quantity + inv.on_hand_quantity
        total_sold = sales_map.get(prod.id, 0.0)
        daily_burn_rate = round(total_sold / 14.0, 2) if total_sold > 0 else 0.5

        if daily_burn_rate > 0:
            days_left = round(total_stock / daily_burn_rate, 1)
        else:
            days_left = 999.0

        min_stock = getattr(prod, "minimum_stock_alert", 10)
        if total_stock == 0:
            risk_level = RiskLevel.CRITICAL
        elif days_left <= 2 or total_stock <= min_stock:
            risk_level = RiskLevel.HIGH
        elif days_left <= 7:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        risks.append({
            "product_id": str(prod.id),
            "product_name": prod.name,
            "product_gtin": prod.gtin,
            "product_sku": prod.gtin,
            "daily_burn_rate": daily_burn_rate,
            "current_total_stock": total_stock,
            "days_until_stockout": days_left,
            "risk_level": risk_level.value
        })

    risks.sort(key=lambda x: (x["days_until_stockout"], x["current_total_stock"]))
    return risks
