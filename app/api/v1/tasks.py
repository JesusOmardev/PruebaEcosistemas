from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional


from ...schemas.task import TaskCreate, TaskOut, TaskUpdateStatus
from ...services.tasks import TaskService
from ...services.typing import get_task_repo
from bson.errors import InvalidId



router = APIRouter(prefix="/tasks", tags=["tasks"])

# app/api/v1/tasks.py
from typing import Optional
...
@router.get("/", response_model=List[TaskOut])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    completed: Optional[bool] = Query(None),
    service: TaskService = Depends(lambda repo=Depends(get_task_repo): TaskService(repo)),
):
    return await service.list(skip=skip, limit=limit, completed=completed)


@router.post("/", response_model=TaskOut, status_code=201)
async def create_task(
    body: TaskCreate,
    service: TaskService = Depends(lambda repo=Depends(get_task_repo): TaskService(repo)),
    ):
    return await service.create(body)


@router.put("/{task_id}", response_model=TaskOut)
async def update_status(
    task_id: str,
    body: TaskUpdateStatus,
    service: TaskService = Depends(lambda repo=Depends(get_task_repo): TaskService(repo)),
    ):
    try:
        return await service.set_completed(task_id, body.completed)
    except (KeyError, InvalidId):
         raise HTTPException(status_code=404, detail="Task not found")


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    service: TaskService = Depends(lambda repo=Depends(get_task_repo): TaskService(repo)),
    ):
    await service.delete(task_id)
    return None