"""Pydantic schemas for the Events module."""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class EventResponse(BaseModel):
    """Schema for a single event in API responses."""
    id: uuid.UUID
    google_event_id: str | None = None
    event_type: str
    title: str
    description: str | None = None
    start_date: datetime
    end_date: datetime
    location: str | None = None
    metadata_info: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    """Schema for paginated event list responses."""
    events: list[EventResponse]
    total: int


class CalendarSyncRequest(BaseModel):
    """Schema for triggering a calendar sync."""
    days_ahead: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Number of days ahead to sync from Google Calendar"
    )
    days_behind: int = Field(
        default=7,
        ge=0,
        le=90,
        description="Number of days in the past to sync from Google Calendar"
    )


class CalendarSyncResponse(BaseModel):
    """Schema for the calendar sync result."""
    synced: int = Field(description="Number of events synced/upserted")
    message: str
