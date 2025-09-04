import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.repositories.base import TaskRepositoryPort
from app.services.typing import get_task_repo 
from typing import Optional, List, Dict
from datetime import datetime, timezone


class InMemoryRepo(TaskRepositoryPort):
    def __init__(self):
        self.items = {}
        self._auto = 0

    async def list(self, skip: int = 0, limit: int = 100, completed: Optional[bool] = None) -> List[Dict]:
        items = list(self.items.values())
        if completed is not None:
            items = [x for x in items if x.get("completed", False) is completed]
        return items[skip: skip + limit]
    
    async def create(self, data: dict):
            self._auto += 1
            _id = str(self._auto)
            obj = {
                "id": _id,
                "title": data["title"],
                "description": data.get("description"),
                "completed": False,
                "creation_date": datetime.now(timezone.utc),
            }
            self.items[_id] = obj
            return obj

    async def set_completed(self, task_id: str, completed: bool):
        if task_id not in self.items:
            raise KeyError
        self.items[task_id]["completed"] = completed
        return self.items[task_id]

    async def delete(self, task_id: str):
        self.items.pop(task_id, None)


    async def update_fields(self, task_id: str, data: Dict) -> Dict:
        if task_id not in self.items:
            raise KeyError
        # aplica solo las claves presentes (como PATCH)
        for k, v in data.items():
            if v is None:
                continue
            self.items[task_id][k] = v
        return self.items[task_id]

_repo_singleton = InMemoryRepo()

def _override_repo():
    # Devolvemos SIEMPRE la misma instancia ya que  el estado persiste entre requests del test
    return _repo_singleton

app.dependency_overrides[get_task_repo] = _override_repo
app.router.on_startup.clear()
app.router.on_shutdown.clear()

# Limpiar repo antes de cada test (no entre requests)
@pytest.fixture(autouse=True)
def _clean_repo():
    _repo_singleton.items.clear()
    _repo_singleton._auto = 0
    yield

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

    #TEST-


def test_create_requires_title_422(client):
    r = client.post("/api/v1/tasks/", json={"description": "sin titulo"})
    assert r.status_code == 422
    data = r.json()
    # Nuestro handler de validación devuelve esta forma
    assert "error" in data and data["error"] in ("ValidationError", "Unprocessable Entity")
    assert "detail" in data

def test_create_title_too_long_422(client):
    long_title = "x" * 201  # schema: max_length=200
    r = client.post("/api/v1/tasks/", json={"title": long_title})
    assert r.status_code == 422

def test_create_description_too_long_422(client):
    long_desc = "x" * 1001  # schema: max_length=1000
    r = client.post("/api/v1/tasks/", json={"title": "ok", "description": long_desc})
    assert r.status_code == 422

def test_create_response_shape_and_defaults(client):
    r = client.post("/api/v1/tasks/", json={"title": "Nueva"})
    assert r.status_code == 201
    data = r.json()
    assert set(("id", "title", "completed", "creation_date")).issubset(data.keys())
    assert data["title"] == "Nueva"
    assert data["completed"] is False
    # creation_date debe ser ISO 8601 parseable
    from datetime import datetime
    datetime.fromisoformat(data["creation_date"].replace("Z", "+00:00"))

def test_update_nonexistent_returns_404(client):
    # En tests usamos repo in-memory; un id que no existe lanza KeyError -> 404
    r = client.put("/api/v1/tasks/9999", json={"completed": True})
    assert r.status_code == 404

def test_delete_is_idempotent_returns_204_twice(client):
    # Creamos
    r = client.post("/api/v1/tasks/", json={"title": "Borrar"})
    tid = r.json()["id"]
    # Delete 1
    r1 = client.delete(f"/api/v1/tasks/{tid}")
    assert r1.status_code == 204
    # Delete 2 (ya no existe) — nuestro repo no falla: sigue 204
    r2 = client.delete(f"/api/v1/tasks/{tid}")
    assert r2.status_code == 204

def test_pagination_skip_limit(client):
    # Crea 7 tareas y verifica 201 en cada POST
    for i in range(7):
        rp = client.post("/api/v1/tasks/", json={"title": f"T{i}"})
        assert rp.status_code == 201, f"POST fallo: {rp.status_code} body={rp.text}"

    # Verifica total = 7 (si esto falla, no hay persistencia entre requests)
    rall = client.get("/api/v1/tasks/")
    assert rall.status_code == 200, rall.text
    all_items = rall.json()
    assert isinstance(all_items, list)
    assert len(all_items) == 7, f"Esperaba 7, obtuve {len(all_items)} -> {all_items}"

    # Página 1: 5 items
    r1 = client.get("/api/v1/tasks/?skip=0&limit=5")
    assert r1.status_code == 200, r1.text
    items1 = r1.json()
    assert isinstance(items1, list) and len(items1) == 5, items1

    # Página 2: 2 restantes
    r2 = client.get("/api/v1/tasks/?skip=5&limit=5")
    assert r2.status_code == 200, r2.text
    items2 = r2.json()
    assert isinstance(items2, list) and len(items2) == 2, items2