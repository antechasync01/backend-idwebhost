"""Repository for ExternalEvent CRUD operations."""

import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.modules.events.infrastructure.models import ExternalEvent


class EventRepository:
    """Data access layer for ExternalEvent model."""

    def __init__(self, db: Session):
        self.db = db

    def upsert_by_google_id(self, google_event_id: str, data: dict) -> ExternalEvent:
        """Insert or update an event based on its Google Calendar event ID.

        Args:
            google_event_id: The unique Google Calendar event ID.
            data: Dict of ExternalEvent fields to set.

        Returns:
            The upserted ExternalEvent instance.
        """
        event = (
            self.db.query(ExternalEvent)
            .filter(ExternalEvent.google_event_id == google_event_id)
            .first()
        )
        if event:
            for key, value in data.items():
                setattr(event, key, value)
        else:
            event = ExternalEvent(google_event_id=google_event_id, **data)
            self.db.add(event)

        self.db.flush()
        return event

    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[ExternalEvent]:
        """Retrieve events overlapping with the given date range."""
        return (
            self.db.query(ExternalEvent)
            .filter(
                ExternalEvent.start_date <= end_date,
                ExternalEvent.end_date >= start_date,
            )
            .order_by(ExternalEvent.start_date.asc())
            .all()
        )

    def get_upcoming(self, from_date: datetime, days: int = 7) -> list[ExternalEvent]:
        """Retrieve events starting within the next N days."""
        from datetime import timedelta

        end_date = from_date + timedelta(days=days)
        return (
            self.db.query(ExternalEvent)
            .filter(
                ExternalEvent.start_date >= from_date,
                ExternalEvent.start_date <= end_date,
            )
            .order_by(ExternalEvent.start_date.asc())
            .all()
        )

    def get_all(self) -> list[ExternalEvent]:
        """Retrieve all events ordered by start_date."""
        return (
            self.db.query(ExternalEvent)
            .order_by(ExternalEvent.start_date.asc())
            .all()
        )

    def count(self) -> int:
        """Return the total count of events."""
        return self.db.query(ExternalEvent).count()
