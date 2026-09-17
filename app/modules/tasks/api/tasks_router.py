import uuid
from typing import Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.responses import success_response
from app.modules.tasks.application.task_service import TaskService
from app.modules.tasks.domain.schemas import (
    TaskAssignStaff,
    TaskCommentCreate,
    TaskCommentResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from app.modules.tasks.infrastructure.models import TaskStatus
from app.modules.users.infrastructure.models import User

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# Helper function to convert DB model to Response DTO
def _to_task_response(db: Session, task: Any) -> TaskResponse:
    created_by = db.get(User, task.created_by_id)
    assigned_to = db.get(User, task.assigned_to_id)
    staff = db.get(User, task.staff_assigned_id) if task.staff_assigned_id else None

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        created_by_id=task.created_by_id,
        created_by_name=created_by.full_name if created_by else None,
        assigned_to_id=task.assigned_to_id,
        assigned_to_name=assigned_to.full_name if assigned_to else None,
        staff_assigned_id=task.staff_assigned_id,
        staff_assigned_name=staff.full_name if staff else None,
        due_date=task.due_date,
        completed_at=task.completed_at,
        notes=task.notes,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def _to_comment_response(db: Session, comment: Any) -> TaskCommentResponse:
    user = db.get(User, comment.user_id)
    return TaskCommentResponse(
        id=comment.id,
        task_id=comment.task_id,
        user_id=comment.user_id,
        user_full_name=user.full_name if user else None,
        content=comment.content,
        created_at=comment.created_at,
    )


# -------------------- Task Endpoints --------------------
@router.post(
    "",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task. Only Owner can create tasks."""
    service = TaskService(db)
    task = service.create_task(payload=payload, created_by=current_user)
    return success_response(
        data=_to_task_response(db, task),
        message="Task created successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "",
    response_model=dict[str, Any],
)
def list_tasks(
    status_filter: TaskStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List tasks filtered by the current user's role."""
    service = TaskService(db)
    items, total = service.list_tasks(
        current_user=current_user,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    data = [_to_task_response(db, t) for t in items]
    return success_response(data=data, meta={"total": total, "skip": skip, "limit": limit})


@router.get(
    "/{task_id}",
    response_model=dict[str, Any],
)
def get_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get task detail. User must be involved in the task."""
    service = TaskService(db)
    task = service.get_task(task_id=task_id, current_user=current_user)
    return success_response(data=_to_task_response(db, task))


@router.put(
    "/{task_id}",
    response_model=dict[str, Any],
)
def update_task(
    task_id: uuid.UUID,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a task. Only Owner can update, and only while PENDING."""
    service = TaskService(db)
    task = service.update_task(task_id=task_id, payload=payload, current_user=current_user)
    return success_response(
        data=_to_task_response(db, task),
        message="Task updated successfully",
    )


@router.post(
    "/{task_id}/accept",
    response_model=dict[str, Any],
)
def accept_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Warehouse Admin accepts a task (PENDING → IN_PROGRESS)."""
    service = TaskService(db)
    task = service.accept_task(task_id=task_id, current_user=current_user)
    return success_response(
        data=_to_task_response(db, task),
        message="Task accepted",
    )


@router.post(
    "/{task_id}/assign-staff",
    response_model=dict[str, Any],
)
def assign_staff(
    task_id: uuid.UUID,
    payload: TaskAssignStaff,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Warehouse Admin assigns a staff member to the task."""
    service = TaskService(db)
    task = service.assign_staff(task_id=task_id, payload=payload, current_user=current_user)
    return success_response(
        data=_to_task_response(db, task),
        message="Staff assigned to task",
    )


@router.post(
    "/{task_id}/complete",
    response_model=dict[str, Any],
)
def complete_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a task as completed. Only assigned admin or staff can complete."""
    service = TaskService(db)
    task = service.complete_task(task_id=task_id, current_user=current_user)
    return success_response(
        data=_to_task_response(db, task),
        message="Task completed",
    )


@router.post(
    "/{task_id}/cancel",
    response_model=dict[str, Any],
)
def cancel_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a task. Only task creator or assigned admin can cancel."""
    service = TaskService(db)
    task = service.cancel_task(task_id=task_id, current_user=current_user)
    return success_response(
        data=_to_task_response(db, task),
        message="Task cancelled",
    )


# -------------------- Comment Endpoints --------------------
@router.post(
    "/{task_id}/comments",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
def add_comment(
    task_id: uuid.UUID,
    payload: TaskCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a comment to a task. User must be involved in the task."""
    service = TaskService(db)
    comment = service.add_comment(task_id=task_id, payload=payload, current_user=current_user)
    return success_response(
        data=_to_comment_response(db, comment),
        message="Comment added",
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/{task_id}/comments",
    response_model=dict[str, Any],
)
def list_comments(
    task_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List comments for a task. User must be involved in the task."""
    service = TaskService(db)
    items, total = service.list_comments(
        task_id=task_id, current_user=current_user, skip=skip, limit=limit
    )
    data = [_to_comment_response(db, c) for c in items]
    return success_response(data=data, meta={"total": total, "skip": skip, "limit": limit})
