from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class TaskOut(TaskBase):
    id: str
    title: str
    description: Optional[str] = None
    completed: bool
    creation_date: datetime 


class TaskUpdateStatus(BaseModel):
    completed: bool

class TaskPatch(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)