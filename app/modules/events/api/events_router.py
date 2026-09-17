"""Events API Router — Endpoint for calendar sync."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.core.responses import create_response
from app.modules.events.application.events_service import EventsService
from app.modules.events.domain.schemas import CalendarSyncRequest
from app.modules.users.infrastructure.models import User

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/sync", status_code=status.HTTP_200_OK)
def sync_calendar(
    body: CalendarSyncRequest = CalendarSyncRequest(),
    current_user: User = Depends(require_permission("analytics.read")),
    db: Session = Depends(get_db),
):
    """Trigger sync from Google Calendar to database (requires analytics.read)."""
    service = EventsService(db)
    synced = service.sync_calendar(
        days_ahead=body.days_ahead,
        days_behind=body.days_behind,
    )
    return create_response(
        data={"synced": synced},
        message=f"Successfully synced {synced} events from Google Calendar",
        status_code=status.HTTP_200_OK,
    )

