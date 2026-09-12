from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.core.responses import create_response
from app.modules.analytics.application.analytics_service import AnalyticsService
from app.modules.users.infrastructure.models import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", status_code=status.HTTP_200_OK)
def get_sales_summary(
    start_date: datetime | None = Query(None, description="Start date for custom filter"),
    end_date: datetime | None = Query(None, description="End date for custom filter"),
    period: str | None = Query("7d", description="Predefined period: today, 7d, 30d, this_month"),
    current_user: User = Depends(require_permission("analytics.read")),
    db: Session = Depends(get_db),
):
    """Retrieve executive sales summary & revenue metrics (requires analytics.read)."""
    service = AnalyticsService(db)
    summary = service.get_sales_summary(start_date=start_date, end_date=end_date, period=period)
    return create_response(
        data=summary,
        status_code=status.HTTP_200_OK,
    )


@router.get("/top-products", status_code=status.HTTP_200_OK)
def get_top_products(
    start_date: datetime | None = Query(None, description="Start date for custom filter"),
    end_date: datetime | None = Query(None, description="End date for custom filter"),
    period: str | None = Query("7d", description="Predefined period: today, 7d, 30d, this_month"),
    limit: int = Query(10, ge=1, le=50, description="Max products to return"),
    current_user: User = Depends(require_permission("analytics.read")),
    db: Session = Depends(get_db),
):
    """Retrieve top-selling products by quantity sold (requires analytics.read)."""
    service = AnalyticsService(db)
    top_products = service.get_top_products(start_date=start_date, end_date=end_date, period=period, limit=limit)
    return create_response(
        data=top_products,
        status_code=status.HTTP_200_OK,
    )


@router.get("/inventory-health", status_code=status.HTTP_200_OK)
def get_inventory_health(
    low_stock_threshold: int = Query(10, ge=1, description="Threshold for low stock alert"),
    current_user: User = Depends(require_permission("analytics.read")),
    db: Session = Depends(get_db),
):
    """Retrieve overall inventory health, valuation, and stock alerts (requires analytics.read)."""
    service = AnalyticsService(db)
    health = service.get_inventory_health(low_stock_threshold=low_stock_threshold)
    return create_response(
        data=health,
        status_code=status.HTTP_200_OK,
    )


@router.get("/sales-trend", status_code=status.HTTP_200_OK)
def get_sales_trend(
    start_date: datetime | None = Query(None, description="Start date for custom filter"),
    end_date: datetime | None = Query(None, description="End date for custom filter"),
    period: str | None = Query("7d", description="Predefined period: today, 7d, 30d, this_month"),
    current_user: User = Depends(require_permission("analytics.read")),
    db: Session = Depends(get_db),
):
    """Retrieve daily sales & refund revenue trend over time (requires analytics.read)."""
    service = AnalyticsService(db)
    trend = service.get_sales_trend(start_date=start_date, end_date=end_date, period=period)
    return create_response(
        data=trend,
        status_code=status.HTTP_200_OK,
    )
