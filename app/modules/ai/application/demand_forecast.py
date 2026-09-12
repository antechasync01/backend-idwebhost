from datetime import date, timedelta
from typing import Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.sales.infrastructure.models import Sale, SaleItem, SaleStatus
from app.modules.products.infrastructure.models import Product


def generate_demand_forecasts(db: Session, product_id: str | None = None, days_ahead: int = 7) -> list[dict[str, Any]]:
    """Generate demand forecast for products for the upcoming N days based on historical sales run-rate."""
    today = date.today()
    start_history = today - timedelta(days=14)

    # Base query for historical sales quantity per product over the last 14 days
    stmt = (
        select(
            Product.id,
            Product.name,
            func.coalesce(func.sum(SaleItem.quantity), 0).label("qty_sold"),
            func.count(func.distinct(Sale.business_date)).label("days_active")
        )
        .join(SaleItem, Product.id == SaleItem.product_id)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.status == SaleStatus.COMPLETED)
        .where(Sale.business_date >= start_history)
        .group_by(Product.id, Product.name)
    )

    if product_id:
        from uuid import UUID
        stmt = stmt.where(Product.id == UUID(product_id))

    rows = db.execute(stmt).all()
    forecasts = []

    for p_id, name, qty_sold, days_active in rows:
        active_days = max(1, days_active)
        daily_avg = float(qty_sold) / float(active_days)

        for d in range(1, days_ahead + 1):
            forecast_date = today + timedelta(days=d)
            # Add small weekend factor if forecast_date is Saturday/Sunday (dayofweek >= 5)
            multiplier = 1.25 if forecast_date.weekday() >= 5 else 1.0
            predicted_qty = round(daily_avg * multiplier, 1)

            forecasts.append({
                "product_id": str(p_id),
                "product_name": name,
                "forecast_date": forecast_date.isoformat(),
                "predicted_quantity": max(1.0, predicted_qty),
                "confidence_score": 0.88 if qty_sold > 10 else 0.70
            })

    return forecasts
