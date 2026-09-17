"""Events Service — Business logic for calendar sync and event queries."""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.modules.events.application.calendar_provider.google.google_calendar import (
    GoogleCalendarProvider,
)
from app.modules.events.infrastructure.repository import EventRepository
from app.modules.ai.application.hermes_agent import HermesAgentService
from app.modules.ai.infrastructure.models import AIInsight, InsightCategory, InsightSeverity
from app.modules.users.infrastructure.models import User, UserRole
from app.modules.events.infrastructure.models import ExternalEvent

logger = logging.getLogger(__name__)


class EventsService:
    """Orchestrates Google Calendar sync and event queries."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = EventRepository(db)

    def sync_calendar(self, days_ahead: int = 30, days_behind: int = 7) -> int:
        """Fetch events from Google Calendar and upsert into the database.

        Args:
            days_ahead: Number of days in the future to fetch.
            days_behind: Number of days in the past to fetch.

        Returns:
            Number of events synced (upserted).
        """
        provider = GoogleCalendarProvider()
        now = datetime.now(timezone.utc)
        time_min = now - timedelta(days=days_behind)
        time_max = now + timedelta(days=days_ahead)

        raw_events = provider.fetch_events(time_min=time_min, time_max=time_max)
        synced_count = 0

        for raw in raw_events:
            google_id = raw.get("id")
            if not google_id:
                logger.warning("Skipping event with missing Google ID")
                continue
            summary = raw.get("summary", "Untitled Event")

            start_info = raw.get("start", {})
            end_info = raw.get("end", {})

            if not start_info or not end_info:
                logger.warning("Skipping event %s — missing start/end", google_id)
                continue

            try:
                start_dt = provider.parse_event_datetime(start_info)
                end_dt = provider.parse_event_datetime(end_info)
            except (ValueError, KeyError) as exc:
                logger.warning("Skipping event %s — bad datetime: %s", google_id, exc)
                continue

            event_type = provider.infer_event_type(summary)

            data = {
                "event_type": event_type,
                "title": summary,
                "description": raw.get("description"),
                "start_date": start_dt,
                "end_date": end_dt,
                "location": raw.get("location"),
                "metadata_info": {
                    "google_calendar_id": raw.get("organizer", {}).get("email"),
                    "html_link": raw.get("htmlLink"),
                    "status": raw.get("status"),
                    "creator": raw.get("creator", {}).get("email"),
                },
            }

            self.repo.upsert_by_google_id(google_id, data)
            synced_count += 1

        self.db.commit()
        logger.info("Calendar sync completed: %d events synced", synced_count)
        return synced_count

    def sync_and_analyze(self, days_ahead: int = 30, days_behind: int = 0) -> tuple[int, int]:
        """Sync calendar and ask Hermes to analyze new unanalyzed events."""
        synced_count = self.sync_calendar(days_ahead=days_ahead, days_behind=days_behind)
        
        # Find unanalyzed events
        unanalyzed_events = self.db.query(ExternalEvent).filter(ExternalEvent.is_analyzed == False).all()
        analyzed_count = 0
        
        if not unanalyzed_events:
            return synced_count, analyzed_count
            
        # Get system owner user context for Hermes
        owner_user = self.db.query(User).filter(User.role_rel.has(code=UserRole.OWNER.value)).first()
        if not owner_user:
            logger.error("Cannot analyze events: No OWNER user found for Hermes context")
            return synced_count, analyzed_count
            
        for event in unanalyzed_events:
            prompt = (
                f"There is a calendar event '{event.title}' scheduled from {event.start_date.strftime('%Y-%m-%d')} "
                f"to {event.end_date.strftime('%Y-%m-%d')} (type: {event.event_type}). "
                f"Based on historical sales data and current stock, please provide an analysis of the impact on sales "
                f"and stock procurement recommendations to prepare for this event."
            )
            
            try:
                # Call Hermes Agent
                response = HermesAgentService.process_chat(
                    db=self.db,
                    user=owner_user,
                    prompt=prompt
                )
                
                # Save as AI Insight with event_date for frontend filtering
                insight = AIInsight(
                    title=f"Event Stock Recommendation: {event.title}",
                    description=response.reply,
                    category=InsightCategory.REORDER,
                    severity=InsightSeverity.INFO,
                    insight_metadata={
                        "event_id": str(event.id),
                        "google_event_id": event.google_event_id,
                        "event_date": event.start_date.isoformat() if event.start_date else None,
                        "source": "auto_detect_calendar"
                    }
                )
                self.db.add(insight)
                
                # Mark as analyzed
                event.is_analyzed = True
                analyzed_count += 1
                self.db.commit()
                
            except Exception as e:
                logger.error("Failed to analyze event %s: %s", event.title, e)
                self.db.rollback()
                
        return synced_count, analyzed_count

    def get_events(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict]:
        """Query events from the database with optional date range filter.

        Returns:
            List of event dicts.
        """
        if start_date and end_date:
            events = self.repo.get_by_date_range(start_date, end_date)
        else:
            events = self.repo.get_all()

        return [self._event_to_dict(e) for e in events]

    def get_upcoming_events(self, days: int = 7) -> list[dict]:
        """Get events starting within the next N days.

        Args:
            days: Number of days ahead to look.

        Returns:
            List of event dicts.
        """
        now = datetime.now(timezone.utc)
        events = self.repo.get_upcoming(from_date=now, days=days)
        return [self._event_to_dict(e) for e in events]

    @staticmethod
    def _event_to_dict(event) -> dict:
        """Convert an ExternalEvent ORM instance to a plain dict."""
        return {
            "id": str(event.id),
            "google_event_id": event.google_event_id,
            "event_type": event.event_type,
            "title": event.title,
            "description": event.description,
            "start_date": event.start_date.isoformat() if event.start_date else None,
            "end_date": event.end_date.isoformat() if event.end_date else None,
            "location": event.location,
            "metadata_info": event.metadata_info,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }
