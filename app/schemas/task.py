# backend/app/schemas/task.py
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=140, description="Short task summary")
    description: str = Field(default="", max_length=2000, description="Detailed markdown/text notes")
    priority: int = Field(default=1, ge=1, le=3, description="1 = Low, 2 = Medium, 3 = High")
    is_completed: bool = Field(default=False)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    """Used for full PUT or partial PATCH updates."""
    title: str | None = Field(default=None, min_length=1, max_length=140)
    description: str | None = Field(default=None, max_length=2000)
    priority: int | None = Field(default=None, ge=1, le=3)
    is_completed: bool | None = None


class TaskResponse(TaskBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)