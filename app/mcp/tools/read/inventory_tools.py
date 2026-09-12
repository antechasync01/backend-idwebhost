from typing import Any
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.inventory.infrastructure.models import Inventory
from app.modules.products.infrastructure.models import Product, Category
from app.modules.sales.infrastructure.models import SaleItem


def get_inventory_stock(db: Session, product_id: str | None = None, category_id: str | None = None) -> list[dict[str, Any]]:
    """Retrieve current inventory levels (display stock and on-hand stock)."""
    stmt = (
        select(Inventory, Product, Category)
        .join(Product, Inventory.product_id == Product.id)
        .outerjoin(Category, Product.category_id == Category.id)
    )

    if product_id:
        stmt = stmt.where(Inventory.product_id == UUID(product_id))
    if category_id:
        stmt = stmt.where(Product.category_id == UUID(category_id))

    results = db.execute(stmt).all()
    out = []
    for inv, prod, cat in results:
        min_stock = getattr(prod, "minimum_stock_alert", 10)
        out.append({
            "product_id": str(prod.id),
            "gtin": prod.gtin,
            "name": prod.name,
            "category_name": cat.name if cat else "Uncategorized",
            "display_quantity": inv.display_quantity,
            "on_hand_quantity": inv.on_hand_quantity,
            "total_quantity": inv.display_quantity + inv.on_hand_quantity,
            "minimum_stock_alert": min_stock,
        })
    return out


def get_stockout_risk_products(db: Session, threshold_days: float = 7.0) -> list[dict[str, Any]]:
    """Calculate and retrieve products with high risk of stockout within specified threshold_days."""
    inventories = db.execute(
        select(Inventory, Product).join(Product, Inventory.product_id == Product.id)
    ).all()

    sales_stmt = select(
        SaleItem.product_id,
        func.sum(SaleItem.quantity).label("total_sold")
    ).group_by(SaleItem.product_id)
    sales_map = {row.product_id: row.total_sold for row in db.execute(sales_stmt).all()}

    risky_products = []
    for inv, prod in inventories:
        total_stock = inv.display_quantity + inv.on_hand_quantity
        total_sold = sales_map.get(prod.id, 0) or 0
        daily_burn_rate = round(total_sold / 14.0, 2) if total_sold > 0 else 0.5

        days_left = round(total_stock / daily_burn_rate, 1) if daily_burn_rate > 0 else 999.0

        min_stock = getattr(prod, "minimum_stock_alert", 10)
        if days_left <= threshold_days or total_stock <= min_stock:
            risk_level = "CRITICAL" if days_left <= 2 or total_stock == 0 else ("HIGH" if days_left <= 5 else "MEDIUM")
            risky_products.append({
                "product_id": str(prod.id),
                "gtin": prod.gtin,
                "name": prod.name,
                "total_stock": total_stock,
                "daily_burn_rate": daily_burn_rate,
                "days_until_stockout": days_left,
                "risk_level": risk_level,
                "recommended_action": f"Buat warehouse request / reorder minimal {max(20, int(daily_burn_rate * 7))} unit"
            })

    risky_products.sort(key=lambda x: x["days_until_stockout"])
    return risky_products
