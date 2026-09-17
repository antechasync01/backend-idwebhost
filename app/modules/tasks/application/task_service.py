import uuid
from datetime import datetime, timezone
from typing import Sequence
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, ValidationError
from app.modules.tasks.domain.exceptions import InvalidTaskStateError, TaskNotFoundError
from app.modules.tasks.domain.schemas import (
    TaskAssignStaff,
    TaskCommentCreate,
    TaskCreate,
    TaskUpdate,
)
from app.modules.tasks.infrastructure.models import Task, TaskComment, TaskPriority, TaskStatus
from app.modules.tasks.infrastructure.task_repository import TaskRepository
from app.modules.users.infrastructure.models import User, UserRole


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TaskRepository(db)

    # -------------------- Create Task (Owner only) --------------------
    def create_task(self, payload: TaskCreate, created_by: User) -> Task:
        """Owner creates a task and assigns it to a Warehouse Admin."""
        if created_by.role != UserRole.OWNER:
            raise ForbiddenError("Only Owner can create tasks.")

        # Validate assigned_to is a WAREHOUSE_ADMIN
        assignee = self.db.get(User, payload.assigned_to_id)
        if not assignee:
            raise ValidationError(f"User '{payload.assigned_to_id}' not found.")
        if assignee.role != UserRole.WAREHOUSE_ADMIN:
            raise ValidationError(
                f"Task can only be assigned to a Warehouse Admin. "
                f"User '{assignee.full_name}' has role '{assignee.role.value if assignee.role else 'None'}'."
            )

        task = Task(
            id=uuid.uuid4(),
            title=payload.title,
            description=payload.description,
            status=TaskStatus.PENDING,
            priority=payload.priority,
            created_by_id=created_by.id,
            assigned_to_id=payload.assigned_to_id,
            due_date=payload.due_date,
            notes=payload.notes,
        )

        self.repo.create_task(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    # -------------------- List Tasks (role-based) --------------------
    def list_tasks(
        self,
        current_user: User,
        status: TaskStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Task], int]:
        """
        List tasks filtered by the user's role:
        - Owner: sees all tasks they created
        - Warehouse Admin: sees tasks assigned to them
        - Warehouse Staff: sees tasks where they are the staff_assigned
        """
        created_by_id = None
        assigned_to_id = None
        staff_assigned_id = None

        if current_user.role == UserRole.OWNER:
            created_by_id = current_user.id
        elif current_user.role == UserRole.WAREHOUSE_ADMIN:
            assigned_to_id = current_user.id
        elif current_user.role == UserRole.WAREHOUSE_STAFF:
            staff_assigned_id = current_user.id
        else:
            # Other roles see nothing
            return [], 0

        return self.repo.list_tasks(
            status=status,
            created_by_id=created_by_id,
            assigned_to_id=assigned_to_id,
            staff_assigned_id=staff_assigned_id,
            skip=skip,
            limit=limit,
        )

    # -------------------- Get Task Detail --------------------
    def get_task(self, task_id: uuid.UUID, current_user: User) -> Task:
        """Get a task by ID. Validates that the user is involved in this task."""
        task = self.repo.get_task_by_id(task_id)
        if not task:
            raise TaskNotFoundError(str(task_id))

        # Check user has access to this task
        self._check_task_access(task, current_user)
        return task

    # -------------------- Update Task (Owner only, while PENDING) --------------------
    def update_task(
        self,
        task_id: uuid.UUID,
        payload: TaskUpdate,
        current_user: User,
    ) -> Task:
        """Owner can update a task while it's still PENDING."""
        if current_user.role != UserRole.OWNER:
            raise ForbiddenError("Only Owner can update tasks.")

        task = self.repo.get_task_by_id(task_id, lock=True)
        if not task:
            raise TaskNotFoundError(str(task_id))

        if task.created_by_id != current_user.id:
            raise ForbiddenError("You can only update tasks you created.")

        if task.status != TaskStatus.PENDING:
            raise InvalidTaskStateError(task.status.value, "update")

        if payload.title is not None:
            task.title = payload.title
        if payload.description is not None:
            task.description = payload.description
        if payload.priority is not None:
            task.priority = payload.priority
        if payload.due_date is not None:
            task.due_date = payload.due_date
        if payload.notes is not None:
            task.notes = payload.notes

        self.repo.update_task(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    # -------------------- Accept Task (Warehouse Admin) --------------------
    def accept_task(self, task_id: uuid.UUID, current_user: User) -> Task:
        """Warehouse Admin accepts a task, changing status from PENDING to IN_PROGRESS."""
        if current_user.role != UserRole.WAREHOUSE_ADMIN:
            raise ForbiddenError("Only Warehouse Admin can accept tasks.")

        task = self.repo.get_task_by_id(task_id, lock=True)
        if not task:
            raise TaskNotFoundError(str(task_id))

        if task.assigned_to_id != current_user.id:
            raise ForbiddenError("This task is not assigned to you.")

        if task.status != TaskStatus.PENDING:
            raise InvalidTaskStateError(task.status.value, "accept")

        task.status = TaskStatus.IN_PROGRESS
        self.repo.update_task(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    # -------------------- Assign Staff (Warehouse Admin) --------------------
    def assign_staff(
        self,
        task_id: uuid.UUID,
        payload: TaskAssignStaff,
        current_user: User,
    ) -> Task:
        """Warehouse Admin assigns a staff member to the task."""
        if current_user.role != UserRole.WAREHOUSE_ADMIN:
            raise ForbiddenError("Only Warehouse Admin can assign staff to tasks.")

        task = self.repo.get_task_by_id(task_id, lock=True)
        if not task:
            raise TaskNotFoundError(str(task_id))

        if task.assigned_to_id != current_user.id:
            raise ForbiddenError("This task is not assigned to you.")

        if task.status not in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
            raise InvalidTaskStateError(task.status.value, "assign_staff")

        # Validate staff exists and has WAREHOUSE_STAFF role
        staff = self.db.get(User, payload.staff_assigned_id)
        if not staff:
            raise ValidationError(f"User '{payload.staff_assigned_id}' not found.")
        if staff.role != UserRole.WAREHOUSE_STAFF:
            raise ValidationError(
                f"Staff must have Warehouse Staff role. "
                f"User '{staff.full_name}' has role '{staff.role.value if staff.role else 'None'}'."
            )

        task.staff_assigned_id = payload.staff_assigned_id

        # Auto-progress to IN_PROGRESS if still PENDING
        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.IN_PROGRESS

        self.repo.update_task(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    # -------------------- Complete Task (Admin or Staff) --------------------
    def complete_task(self, task_id: uuid.UUID, current_user: User) -> Task:
        """Warehouse Admin or assigned Staff marks a task as completed."""
        task = self.repo.get_task_by_id(task_id, lock=True)
        if not task:
            raise TaskNotFoundError(str(task_id))

        # Only the assigned admin or assigned staff can complete
        is_admin = current_user.id == task.assigned_to_id
        is_staff = current_user.id == task.staff_assigned_id

        if not (is_admin or is_staff):
            raise ForbiddenError("Only the assigned admin or staff can complete this task.")

        if task.status != TaskStatus.IN_PROGRESS:
            raise InvalidTaskStateError(task.status.value, "complete")

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now(timezone.utc)
        self.repo.update_task(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    # -------------------- Cancel Task (Owner or Admin) --------------------
    def cancel_task(self, task_id: uuid.UUID, current_user: User) -> Task:
        """Owner or assigned Admin can cancel a task."""
        task = self.repo.get_task_by_id(task_id, lock=True)
        if not task:
            raise TaskNotFoundError(str(task_id))

        is_owner = current_user.id == task.created_by_id
        is_admin = current_user.id == task.assigned_to_id

        if not (is_owner or is_admin):
            raise ForbiddenError("Only the task creator or assigned admin can cancel this task.")

        if task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            raise InvalidTaskStateError(task.status.value, "cancel")

        task.status = TaskStatus.CANCELLED
        self.repo.update_task(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    # -------------------- Comments --------------------
    def add_comment(
        self,
        task_id: uuid.UUID,
        payload: TaskCommentCreate,
        current_user: User,
    ) -> TaskComment:
        """Add a comment to a task. User must be involved in the task."""
        task = self.repo.get_task_by_id(task_id)
        if not task:
            raise TaskNotFoundError(str(task_id))

        self._check_task_access(task, current_user)

        comment = TaskComment(
            id=uuid.uuid4(),
            task_id=task_id,
            user_id=current_user.id,
            content=payload.content,
        )

        self.repo.create_comment(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def list_comments(
        self,
        task_id: uuid.UUID,
        current_user: User,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[TaskComment], int]:
        """List comments for a task. User must be involved in the task."""
        task = self.repo.get_task_by_id(task_id)
        if not task:
            raise TaskNotFoundError(str(task_id))

        self._check_task_access(task, current_user)
        return self.repo.list_comments(task_id=task_id, skip=skip, limit=limit)

    # -------------------- Internal Helpers --------------------
    def _check_task_access(self, task: Task, user: User) -> None:
        """Ensure user is involved in this task (creator, assignee, or staff)."""
        involved = (
            user.id == task.created_by_id
            or user.id == task.assigned_to_id
            or user.id == task.staff_assigned_id
        )
        if not involved:
            raise ForbiddenError("You do not have access to this task.")
