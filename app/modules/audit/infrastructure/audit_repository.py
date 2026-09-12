import uuid
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.modules.audit.infrastructure.models import ActorType, AuditLog


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        action: str,
        entity_type: str,
        actor_id: uuid.UUID | None = None,
        actor_type: ActorType = ActorType.SYSTEM,
        entity_id: uuid.UUID | None = None,
        before_data: dict | None = None,
        after_data: dict | None = None,
        metadata_info: dict | None = None,
    ) -> AuditLog:
        log_entry = AuditLog(
            id=uuid.uuid4(),
            actor_id=actor_id,
            actor_type=actor_type,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_data=before_data,
            after_data=after_data,
            metadata_info=metadata_info,
        )
        self.db.add(log_entry)
        self.db.flush()
        return log_entry

    def get_by_id(self, log_id: uuid.UUID) -> AuditLog | None:
        return self.db.query(AuditLog).filter(AuditLog.id == log_id).first()

    def list_logs(
        self,
        actor_id: uuid.UUID | None = None,
        actor_type: ActorType | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[AuditLog], int]:
        query = self.db.query(AuditLog)

        if actor_id:
            query = query.filter(AuditLog.actor_id == actor_id)
        if actor_type:
            query = query.filter(AuditLog.actor_type == actor_type)
        if action:
            query = query.filter(AuditLog.action.ilike(f"%{action}%"))
        if entity_type:
            query = query.filter(AuditLog.entity_type.ilike(f"%{entity_type}%"))
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)

        total = query.count()
        logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()

        return logs, total
