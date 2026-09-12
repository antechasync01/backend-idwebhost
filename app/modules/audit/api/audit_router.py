import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.core.responses import create_response
from app.modules.audit.application.audit_service import AuditService
from app.modules.audit.infrastructure.models import ActorType
from app.modules.users.infrastructure.models import User

router = APIRouter(prefix="/audit", tags=["Audit Log"])


@router.get("/logs", status_code=status.HTTP_200_OK)
def list_audit_logs(
    actor_id: uuid.UUID | None = Query(None, description="Filter by actor ID"),
    actor_type: ActorType | None = Query(None, description="Filter by actor type"),
    action: str | None = Query(None, description="Filter by action name"),
    entity_type: str | None = Query(None, description="Filter by entity type"),
    entity_id: uuid.UUID | None = Query(None, description="Filter by entity ID"),
    start_date: datetime | None = Query(None, description="Filter start timestamp"),
    end_date: datetime | None = Query(None, description="Filter end timestamp"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_permission("audit.read")),
    db: Session = Depends(get_db),
):
    """Retrieve audit logs with optional filtering and pagination (requires audit.read)."""
    service = AuditService(db)
    result = service.list_logs(
        actor_id=actor_id,
        actor_type=actor_type,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
    return create_response(
        data=result,
        status_code=status.HTTP_200_OK,
    )


@router.get("/logs/{log_id}", status_code=status.HTTP_200_OK)
def get_audit_log(
    log_id: uuid.UUID,
    current_user: User = Depends(require_permission("audit.read")),
    db: Session = Depends(get_db),
):
    """Get detailed audit log by ID (requires audit.read)."""
    service = AuditService(db)
    log_detail = service.get_log_by_id(log_id)
    return create_response(
        data=log_detail,
        status_code=status.HTTP_200_OK,
    )
