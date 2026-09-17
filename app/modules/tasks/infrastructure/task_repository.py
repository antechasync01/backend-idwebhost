import uuid
from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.modules.tasks.infrastructure.models import Task, TaskComment, TaskStatus


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task: Task) -> Task:
        self.db.add(task)
        self.db.flush()
        return task

    def get_task_by_id(self, task_id: uuid.UUID, lock: bool = False) -> Task | None:
        stmt = select(Task).where(Task.id == task_id)
        if lock:
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

    def list_tasks(
        self,
        status: TaskStatus | None = None,
        created_by_id: uuid.UUID | None = None,
        assigned_to_id: uuid.UUID | None = None,
        staff_assigned_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Task], int]:
        stmt = select(Task)

        if status:
            stmt = stmt.where(Task.status == status)
        if created_by_id:
            stmt = stmt.where(Task.created_by_id == created_by_id)
        if assigned_to_id:
            stmt = stmt.where(Task.assigned_to_id == assigned_to_id)
        if staff_assigned_id:
            stmt = stmt.where(Task.staff_assigned_id == staff_assigned_id)

        # Count total matching rows
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_stmt) or 0

        # Apply pagination
        paginated_stmt = stmt.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        items = self.db.scalars(paginated_stmt).all()
        return items, total

    def update_task(self, task: Task) -> Task:
        self.db.flush()
        return task

    # ---------------- Task Comments ----------------
    def create_comment(self, comment: TaskComment) -> TaskComment:
        self.db.add(comment)
        self.db.flush()
        return comment

    def list_comments(
        self,
        task_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[TaskComment], int]:
        stmt = select(TaskComment).where(TaskComment.task_id == task_id)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_stmt) or 0

        paginated_stmt = stmt.order_by(TaskComment.created_at.asc()).offset(skip).limit(limit)
        items = self.db.scalars(paginated_stmt).all()
        return items, total
