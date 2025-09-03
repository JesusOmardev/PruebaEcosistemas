from ..db.mongodb import get_tasks_collection
from ..db.repositories.tasks import TaskRepository

def get_task_repo():
    col = get_tasks_collection()
    return TaskRepository(col)
