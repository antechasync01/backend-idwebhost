import math
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.modules.audit.domain.exceptions import AuditLogNotFoundError
from app.modules.audit.domain.schemas import AuditLogListResponse, AuditLogResponse
from app.modules.audit.infrastructure.audit_repository import AuditRepository
from app.modules.audit.infrastructure.models import ActorType


class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = AuditRepository(db)

    def log_event(
        self,
        action: str,
        entity_type: str,
        actor_id: uuid.UUID | None = None,
        actor_type: ActorType = ActorType.SYSTEM,
        entity_id: uuid.UUID | None = None,
        before_data: dict | None = None,
        after_data: dict | None = None,
        metadata_info: dict | None = None,
    ) -> AuditLogResponse:
        log_entry = self.repository.create(
            action=action,
            entity_type=entity_type,
            actor_id=actor_id,
            actor_type=actor_type,
            entity_id=entity_id,
            before_data=before_data,
            after_data=after_data,
            metadata_info=metadata_info,
        )
        self.db.commit()
        self.db.refresh(log_entry)
        return AuditLogResponse.model_validate(log_entry)

    def get_log_by_id(self, log_id: uuid.UUID) -> AuditLogResponse:
        log_entry = self.repository.get_by_id(log_id)
        if not log_entry:
            raise AuditLogNotFoundError(str(log_id))
        return AuditLogResponse.model_validate(log_entry)

    def list_logs(
        self,
        actor_id: uuid.UUID | None = None,
        actor_type: ActorType | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> AuditLogListResponse:
        skip = (page - 1) * page_size
        logs, total = self.repository.list_logs(
            actor_id=actor_id,
            actor_type=actor_type,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=page_size,
        )
        items = [AuditLogResponse.model_validate(log) for log in logs]
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return AuditLogListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
