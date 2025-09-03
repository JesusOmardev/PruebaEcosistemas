from ..db.repositories.base import TaskRepositoryPort
from ..schemas.task import TaskCreate

class TaskService:
    def __init__(self, repo: TaskRepositoryPort):
        self.repo = repo

    async def list(self, skip: int = 0, limit: int = 100):
        return await self.repo.list(skip=skip, limit=limit)

    async def create(self, data: TaskCreate):
        # Pydantic v2
        return await self.repo.create(data.model_dump())

    async def set_completed(self, task_id: str, completed: bool):
        return await self.repo.set_completed(task_id, completed)

    async def delete(self, task_id: str):
        await self.repo.delete(task_id)