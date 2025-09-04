from typing import List, Dict, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from .base import TaskRepositoryPort

class TaskRepository(TaskRepositoryPort):
    def __init__(self, col: AsyncIOMotorCollection):
        self.col = col

    def _to_out(self, doc: Dict) -> Dict:
        return {
            "id": str(doc["_id"]),
            "title": doc["title"],
            "description": doc.get("description"),
            "completed": doc.get("completed", False),
            "creation_date": doc.get("creation_date"),
        }

    async def list(self, skip: int = 0, limit: int = 100, completed: Optional[bool] = None) -> List[Dict]:
        q = {} if completed is None else {"completed": completed}
        cursor = self.col.find(q).sort("creation_date", -1).skip(skip).limit(limit)
        return [self._to_out(d) async for d in cursor]


    async def create(self, data: Dict) -> Dict:
        payload = {**data}
        payload.setdefault("completed", False)
        res = await self.col.insert_one(payload)
        doc = await self.col.find_one({"_id": res.inserted_id})
        return self._to_out(doc)

    async def set_completed(self, task_id: str, completed: bool) -> Dict:
        oid = ObjectId(task_id)
        await self.col.update_one({"_id": oid}, {"$set": {"completed": completed}})
        doc = await self.col.find_one({"_id": oid})
        if not doc:
            raise KeyError("Task not found")
        return self._to_out(doc)

    async def delete(self, task_id: str) -> None:
        oid = ObjectId(task_id)
        await self.col.delete_one({"_id": oid})
