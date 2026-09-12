from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.modules.notifications.infrastructure.models import NotificationType
from app.modules.users.infrastructure.models import UserRole


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID | None = None
    target_role: UserRole | None = None
    title: str
    message: str
    type: NotificationType
    is_read: bool
    payload: dict | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationUpdate(BaseModel):
    is_read: bool = True
