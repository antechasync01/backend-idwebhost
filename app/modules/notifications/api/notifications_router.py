from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError
from app.core.responses import create_response
from app.modules.notifications.infrastructure.models import Notification
from app.modules.users.infrastructure.models import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", status_code=status.HTTP_200_OK)
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_role = current_user.role
    conditions = [Notification.user_id == current_user.id]
    if user_role:
        conditions.append(Notification.target_role == user_role)

    stmt = (
        select(Notification)
        .where(or_(*conditions))
        .order_by(Notification.created_at.desc())
        .limit(20)
    )

    notifications = db.execute(stmt).scalars().all()
    out = []
    for n in notifications:
        out.append({
            "id": str(n.id),
            "title": n.title,
            "message": n.message,
            "type": n.type.value,
            "is_read": n.is_read,
            "payload": n.payload,
            "created_at": n.created_at.isoformat()
        })

    return create_response(
        data=out,
        status_code=status.HTTP_200_OK,
    )


@router.patch("/{notification_id}/read", status_code=status.HTTP_200_OK)
def mark_notification_as_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a notification as read."""
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise NotFoundError("Notification not found")

    notif.is_read = True
    db.commit()

    return create_response(
        data={"id": str(notif.id), "is_read": True},
        meta={"message": "Notification marked as read"},
        status_code=status.HTTP_200_OK,
    )
