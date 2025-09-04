from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class TaskRepositoryPort(ABC):
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100, completed: Optional[bool] = None) -> List[Dict]: 
        ...
    @abstractmethod
    async def create(self, data: Dict) -> Dict: 
        ...
    @abstractmethod
    async def set_completed(self, task_id: str, completed: bool) -> Dict: 
        ...
    @abstractmethod
    async def delete(self, task_id: str) -> None: 
        ...
    @abstractmethod
    async def update_fields(self, task_id: str, data: Dict) -> Dict: 
        ...
