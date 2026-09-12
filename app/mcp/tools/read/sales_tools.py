from typing import Any
from datetime import date, datetime
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session

from app.modules.sales.infrastructure.models import Sale, SaleItem, SaleStatus
from app.modules.products.infrastructure.models import Product


def get_sales_summary(db: Session, start_date: str | None = None, end_date: str | None = None) -> dict[str, Any]:
    """Retrieve aggregated sales summary including total revenue, transaction count, and average basket size."""
    stmt = select(
        func.count(Sale.id).label("transaction_count"),
        func.coalesce(func.sum(Sale.total_amount), 0.0).label("total_revenue"),
        func.coalesce(func.avg(Sale.total_amount), 0.0).label("average_basket")
    ).where(Sale.status == SaleStatus.COMPLETED)

    if start_date:
        stmt = stmt.where(Sale.business_date >= date.fromisoformat(start_date))
    if end_date:
        stmt = stmt.where(Sale.business_date <= date.fromisoformat(end_date))

    row = db.execute(stmt).one()
    return {
        "transaction_count": row.transaction_count,
        "total_revenue": float(row.total_revenue),
        "average_basket": round(float(row.average_basket), 2),
        "start_date": start_date or "All time",
        "end_date": end_date or "All time",
    }


def get_top_selling_products(db: Session, limit: int = 5) -> list[dict[str, Any]]:
    """Retrieve top selling products by quantity sold."""
    stmt = (
        select(
            Product.id,
            Product.gtin,
            Product.name,
            func.sum(SaleItem.quantity).label("total_quantity_sold"),
            func.sum(SaleItem.subtotal).label("total_revenue")
        )
        .join(SaleItem, Product.id == SaleItem.product_id)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.status == SaleStatus.COMPLETED)
        .group_by(Product.id, Product.gtin, Product.name)
        .order_by(desc("total_quantity_sold"))
        .limit(limit)
    )

    results = db.execute(stmt).all()
    out = []
    for prod_id, gtin, name, qty_sold, revenue in results:
        out.append({
            "product_id": str(prod_id),
            "gtin": gtin,
            "name": name,
            "quantity_sold": int(qty_sold or 0),
            "total_revenue": float(revenue or 0.0)
        })
    return out
