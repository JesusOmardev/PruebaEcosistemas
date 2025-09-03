from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class TaskCreate(TaskBase):
    creation_date: datetime = Field(default_factory=datetime.utcnow)


class TaskOut(TaskBase):
    id: str
    completed: bool
    creation_date: datetime


class TaskUpdateStatus(BaseModel):
    completed: bool