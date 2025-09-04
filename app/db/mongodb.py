from motor.motor_asyncio import AsyncIOMotorClient
from ..core import config

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    assert _client is not None, "Mongo client not initialized"
    return _client


async def connect() -> None:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(config.MONGO_URI)


async def disconnect() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None

    col = get_tasks_collection()
    await col.create_index("creation_date")
    await col.create_index("completed")

def get_db():
    return get_client()[config.MONGO_DB]


def get_tasks_collection():
    return get_db()["tasks"]


async def ensure_indexes() -> None:
    # Si no hay cliente, por ejemplo  en tests con repo in-memory, salimos sin hacer nada
    if _client is None:
        return
    db = _client[config.MONGO_DB]
    col = db["tasks"]
    # Índices básicos
    await col.create_index("creation_date")
    await col.create_index("completed")