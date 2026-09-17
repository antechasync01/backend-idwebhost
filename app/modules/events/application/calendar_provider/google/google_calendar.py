"""Google Calendar Provider — Fetches events using Google Calendar API with OAuth2."""

from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.core.config import settings


class GoogleCalendarProvider:
    """Fetches events from Google Calendar using OAuth2 refresh token."""

    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

    def __init__(self):
        self._credentials = Credentials(
            token=None,
            refresh_token=settings.GOOGLE_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=self.SCOPES,
        )
        self._service = build("calendar", "v3", credentials=self._credentials)

    def fetch_events(
        self,
        time_min: datetime | None = None,
        time_max: datetime | None = None,
        calendar_id: str = "primary",
        max_results: int = 100,
    ) -> list[dict]:
        """Fetch events from Google Calendar within the given time range.

        Args:
            time_min: Start of time range (defaults to now).
            time_max: End of time range (optional, no upper bound if None).
            calendar_id: Google Calendar ID (defaults to 'primary').
            max_results: Maximum number of events to return.

        Returns:
            List of raw Google Calendar event dicts.
        """
        if time_min is None:
            time_min = datetime.now(timezone.utc)

        params: dict = {
            "calendarId": calendar_id,
            "timeMin": time_min.isoformat(),
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime",
        }
        if time_max is not None:
            params["timeMax"] = time_max.isoformat()

        result = self._service.events().list(**params).execute()
        return result.get("items", [])

    @staticmethod
    def parse_event_datetime(dt_info: dict) -> datetime:
        """Parse Google Calendar dateTime or date field into a timezone-aware datetime."""
        if "dateTime" in dt_info:
            return datetime.fromisoformat(dt_info["dateTime"])
        # All-day events only have 'date' (YYYY-MM-DD)
        return datetime.strptime(dt_info["date"], "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )

    @staticmethod
    def infer_event_type(summary: str) -> str:
        """Infer event_type from the event summary/title using keyword matching."""
        lower = summary.lower()

        holiday_keywords = ["libur", "holiday", "cuti", "hari raya", "tahun baru", "natal", "lebaran", "imlek"]
        promo_keywords = ["promo", "diskon", "sale", "flash sale", "harbolnas", "gajian"]
        meeting_keywords = ["meeting", "rapat", "standup", "sync", "review"]

        for kw in holiday_keywords:
            if kw in lower:
                return "holiday"
        for kw in promo_keywords:
            if kw in lower:
                return "promo"
        for kw in meeting_keywords:
            if kw in lower:
                return "meeting"

        return "general"