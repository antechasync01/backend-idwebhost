import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.modules.analytics.infrastructure.models import PeriodicAnalysis, AnalysisPeriod
from app.modules.analytics.application.analytics_service import AnalyticsService
from app.modules.ai.application.hermes_agent import HermesAgentService
from app.modules.users.infrastructure.models import User, UserRole


class PeriodicAnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.analytics_svc = AnalyticsService(db)

    def generate_analysis(self, period_type: AnalysisPeriod) -> PeriodicAnalysis | None:
        """Generates analysis by querying analytics service and sending to Hermes."""
        
        # Determine the period string
        period_str = "7d" if period_type == AnalysisPeriod.WEEKLY else "30d"
        
        # 1. Fetch raw data
        sales_summary = self.analytics_svc.get_sales_summary(period=period_str)
        top_products = self.analytics_svc.get_top_products(period=period_str, limit=5)
        sales_trend = self.analytics_svc.get_sales_trend(period=period_str)
        
        # Compile raw data for prompt and storage
        raw_data = {
            "summary": {
                "net_revenue": str(sales_summary.net_revenue),
                "transaction_count": sales_summary.transaction_count,
                "average_transaction_value": str(sales_summary.average_transaction_value)
            },
            "top_products": [
                {"name": p.product_name, "quantity": p.quantity_sold, "revenue": str(p.total_revenue)}
                for p in top_products.items
            ],
            "trends": [
                {"date": t.date, "sales": str(t.net_revenue)}
                for t in sales_trend.items
            ]
        }

        raw_data_str = json.dumps(raw_data, indent=2)

        # 2. Prepare Prompt based on period
        if period_type == AnalysisPeriod.WEEKLY:
            prompt = (
                f"Berikut adalah ringkasan data penjualan selama 7 hari terakhir: \n{raw_data_str}\n\n"
                "Tolong berikan analisis singkat mengenai performa penjualan minggu ini, tren harian yang terlihat, "
                "dan rekomendasi taktis untuk minggu depan."
            )
        else:
            prompt = (
                f"Berikut adalah ringkasan data penjualan selama 30 hari terakhir: \n{raw_data_str}\n\n"
                "Tolong berikan analisis strategis komprehensif, evaluasi produk unggulan, "
                "serta saran pengadaan stok (procurement) untuk bulan depan."
            )

        # 3. Call Hermes Agent
        # Get a system/owner user to act as context for Hermes
        owner_user = self.db.query(User).filter(User.role_rel.has(code=UserRole.OWNER.value)).first()
        if not owner_user:
            return None # Cannot run without an owner context

        hermes_resp = HermesAgentService.process_chat(
            db=self.db,
            user=owner_user,
            prompt=prompt
        )

        analysis_text = hermes_resp.reply

        # 4. Save to Database
        periodic_analysis = PeriodicAnalysis(
            period_type=period_type,
            start_date=sales_summary.start_date,
            end_date=sales_summary.end_date,
            raw_data=raw_data,
            analysis_result=analysis_text
        )
        self.db.add(periodic_analysis)
        self.db.commit()
        self.db.refresh(periodic_analysis)

        return periodic_analysis

    def get_latest_analysis(self, period_type: AnalysisPeriod) -> PeriodicAnalysis | None:
        """Retrieves the most recent analysis for a given period type."""
        return (
            self.db.query(PeriodicAnalysis)
            .filter(PeriodicAnalysis.period_type == period_type)
            .order_by(PeriodicAnalysis.generated_at.desc())
            .first()
        )
