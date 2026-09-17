"""CalendarProvider — Facade for calendar event sync operations."""

from sqlalchemy.orm import Session


class CalendarProvider:
    """High-level facade for calendar sync operations.

    Wraps EventsService for simpler usage from external callers.
    Lazy import to avoid circular dependencies.
    """

    def __init__(self, db: Session):
        self._db = db

    def _get_service(self):
        from app.modules.events.application.events_service import EventsService
        return EventsService(self._db)

    def sync(self, days_ahead: int = 30, days_behind: int = 7) -> int:
        """Sync events from Google Calendar to the database."""
        return self._get_service().sync_calendar(
            days_ahead=days_ahead,
            days_behind=days_behind,
        )

    def get_upcoming(self, days: int = 7) -> list[dict]:
        """Get upcoming events within N days."""
        return self._get_service().get_upcoming_events(days=days)
