from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.responses import create_response
from app.modules.users.infrastructure.models import User
from app.modules.ai.api.schemas import HermesChatRequest
from app.modules.ai.application.demand_forecast import generate_demand_forecasts
from app.modules.ai.application.stockout_risk import calculate_stockout_risks
from app.modules.ai.application.insight_generator import generate_and_sync_ai_insights
from app.modules.ai.application.hermes_agent import HermesAgentService

router = APIRouter(prefix="/ai", tags=["AI Intelligence & Hermes"])


@router.get("/insights", status_code=status.HTTP_200_OK)
def get_ai_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve AI-generated business insights and reorder alerts."""
    insights = generate_and_sync_ai_insights(db)
    return create_response(
        data=insights,
        status_code=status.HTTP_200_OK,
    )


@router.get("/stockout-risk", status_code=status.HTTP_200_OK)
def get_stockout_risks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve stockout risk calculations for all inventory items."""
    risks = calculate_stockout_risks(db)
    return create_response(
        data=risks,
        status_code=status.HTTP_200_OK,
    )


@router.get("/forecasts", status_code=status.HTTP_200_OK)
def get_demand_forecasts(
    product_id: str | None = Query(None, description="Optional product UUID filter"),
    days_ahead: int = Query(7, ge=1, le=30, description="Forecast horizon in days"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve demand forecast for products."""
    forecasts = generate_demand_forecasts(db, product_id=product_id, days_ahead=days_ahead)
    return create_response(
        data=forecasts,
        status_code=status.HTTP_200_OK,
    )


@router.post("/hermes/chat", status_code=status.HTTP_200_OK)
def hermes_chat(
    request: HermesChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Conversational reasoning API endpoint with Hermes Agent (inherits JWT user context)."""
    response = HermesAgentService.process_chat(
        db=db,
        user=current_user,
        prompt=request.prompt,
        conversation_id=request.conversation_id,
    )
    return create_response(
        data=response.model_dump(),
        status_code=status.HTTP_200_OK,
    )
