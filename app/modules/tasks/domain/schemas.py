from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.modules.tasks.infrastructure.models import TaskStatus, TaskPriority


# ---------------- Task Schemas ----------------
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Judul task")
    description: str | None = Field(None, description="Detail instruksi task")
    assigned_to_id: uuid.UUID = Field(..., description="ID Admin Gudang yang ditugaskan")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Prioritas task")
    due_date: datetime | None = Field(None, description="Deadline task (optional)")
    notes: str | None = Field(None, description="Catatan tambahan")


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    notes: str | None = None


class TaskAssignStaff(BaseModel):
    staff_assigned_id: uuid.UUID = Field(..., description="ID Staff Gudang yang ditugaskan")


class TaskCommentCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Isi comment")


# ---------------- Response Schemas ----------------
class TaskCommentResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    user_id: uuid.UUID
    user_full_name: str | None = None
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    status: TaskStatus
    priority: TaskPriority
    created_by_id: uuid.UUID
    created_by_name: str | None = None
    assigned_to_id: uuid.UUID
    assigned_to_name: str | None = None
    staff_assigned_id: uuid.UUID | None = None
    staff_assigned_name: str | None = None
    due_date: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
