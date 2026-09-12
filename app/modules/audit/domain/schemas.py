import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.modules.audit.infrastructure.models import ActorType


class AuditLogCreate(BaseModel):
    actor_id: uuid.UUID | None = None
    actor_type: ActorType = ActorType.SYSTEM
    action: str = Field(..., max_length=100)
    entity_type: str = Field(..., max_length=100)
    entity_id: uuid.UUID | None = None
    before_data: dict | None = None
    after_data: dict | None = None
    metadata_info: dict | None = None


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actor_id: uuid.UUID | None = None
    actor_type: ActorType
    action: str
    entity_type: str
    entity_id: uuid.UUID | None = None
    before_data: dict | None = None
    after_data: dict | None = None
    metadata_info: dict | None = None
    timestamp: datetime


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
