from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.modules.analytics.domain.exceptions import InvalidDateRangeError
from app.modules.analytics.domain.schemas import (
    DailySalesTrendItem,
    InventoryHealthResponse,
    SalesSummaryResponse,
    SalesTrendResponse,
    TopProductItem,
    TopProductsResponse,
)
from app.modules.analytics.infrastructure.analytics_repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = AnalyticsRepository(db)

    def _resolve_date_range(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        period: str | None = "7d",
    ) -> tuple[datetime, datetime]:
        now = datetime.now(timezone.utc)

        if start_date and end_date:
            if start_date > end_date:
                raise InvalidDateRangeError("Start date cannot be after end date.")
            return start_date, end_date

        if period == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return start, now
        elif period == "30d":
            start = now - timedelta(days=30)
            return start, now
        elif period == "this_month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return start, now
        else:  # Default "7d"
            start = now - timedelta(days=7)
            return start, now

    def get_sales_summary(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        period: str | None = "7d",
    ) -> SalesSummaryResponse:
        start, end = self._resolve_date_range(start_date, end_date, period)
        summary_data = self.repository.get_sales_summary(start, end)
        return SalesSummaryResponse(
            **summary_data,
            start_date=start,
            end_date=end,
        )

    def get_top_products(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        period: str | None = "7d",
        limit: int = 10,
    ) -> TopProductsResponse:
        start, end = self._resolve_date_range(start_date, end_date, period)
        items_data = self.repository.get_top_selling_products(start, end, limit=limit)
        items = [TopProductItem(**item) for item in items_data]
        return TopProductsResponse(
            items=items,
            start_date=start,
            end_date=end,
        )

    def get_inventory_health(self, low_stock_threshold: int = 10) -> InventoryHealthResponse:
        health_data = self.repository.get_inventory_health(low_stock_threshold=low_stock_threshold)
        return InventoryHealthResponse(**health_data)

    def get_sales_trend(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        period: str | None = "7d",
    ) -> SalesTrendResponse:
        start, end = self._resolve_date_range(start_date, end_date, period)
        trend_items_data = self.repository.get_daily_sales_trend(start, end)
        items = [DailySalesTrendItem(**item) for item in trend_items_data]
        return SalesTrendResponse(
            items=items,
            start_date=start,
            end_date=end,
        )
