from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.ai.application.stockout_risk import calculate_stockout_risks
from app.modules.ai.infrastructure.models import AIInsight, InsightCategory, InsightSeverity
from app.modules.notifications.infrastructure.models import Notification, NotificationType
from app.modules.users.infrastructure.models import UserRole


def generate_and_sync_ai_insights(db: Session) -> list[dict[str, Any]]:
    """Scan inventory and sales metrics, generate AI Insights, and create notifications for Owner & Warehouse Admin."""
    risks = calculate_stockout_risks(db)
    high_risks = [r for r in risks if r["risk_level"] in ("CRITICAL", "HIGH")]

    insights_data = []

    for risk in high_risks:
        p_name = risk["product_name"]
        days = risk["days_until_stockout"]
        stock = risk["current_total_stock"]
        burn = risk["daily_burn_rate"]

        title = f"Peringatan Stok Kritis: {p_name}"
        desc = (
            f"Stok produk {p_name} tersisa {stock} unit dengan rata-rata penjualan {burn} unit/hari. "
            f"Diproyeksikan akan habis dalam {days} hari."
        )
        action = f"Segera ajukan pengadaan / warehouse request minimal {max(20, int(burn * 7))} unit."

        # Create or update AIInsight
        insight = AIInsight(
            title=title,
            description=desc,
            category=InsightCategory.RISK,
            severity=InsightSeverity.CRITICAL if risk["risk_level"] == "CRITICAL" else InsightSeverity.WARNING,
            action_recommended=action,
            insight_metadata=risk
        )
        db.add(insight)

        # Dispatch Notification to Owner & Warehouse Admin
        notif = Notification(
            target_role=UserRole.OWNER,
            title=title,
            message=desc,
            type=NotificationType.STOCKOUT_RISK,
            payload=risk
        )
        db.add(notif)

    db.commit()

    # Query active insights
    results = db.execute(select(AIInsight).order_by(AIInsight.created_at.desc()).limit(10)).scalars().all()
    out = []
    for item in results:
        out.append({
            "id": str(item.id),
            "title": item.title,
            "description": item.description,
            "category": item.category.value,
            "severity": item.severity.value,
            "action_recommended": item.action_recommended,
            "created_at": item.created_at.isoformat()
        })
    return out
