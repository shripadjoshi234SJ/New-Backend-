from typing import Any, Dict, List

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


class InMemoryCollection:
    def __init__(self) -> None:
        self._items: List[Dict[str, Any]] = []

    async def find_one(self, query: Dict[str, Any]) -> Dict[str, Any] | None:
        for item in self._items:
            if all(item.get(key) == value for key, value in query.items()):
                return item
        return None

    async def insert_one(self, document: Dict[str, Any]) -> None:
        self._items.append(document)

    async def find(self, query: Dict[str, Any] | None = None):
        query = query or {}

        async def generator():
            for item in self._items:
                if all(item.get(key) == value for key, value in query.items()):
                    yield item

        return generator()

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> None:
        for item in self._items:
            if all(item.get(key) == value for key, value in query.items()):
                for key, value in update.get("$set", {}).items():
                    item[key] = value
                break

    async def delete_one(self, query: Dict[str, Any]) -> Any:
        for index, item in enumerate(self._items):
            if all(item.get(key) == value for key, value in query.items()):
                del self._items[index]
                return type("Result", (), {"deleted_count": 1})()
        return type("Result", (), {"deleted_count": 0})()


class InMemoryDatabase:
    def __init__(self) -> None:
        self._collections: Dict[str, InMemoryCollection] = {}

    def __getitem__(self, name: str) -> InMemoryCollection:
        if name not in self._collections:
            self._collections[name] = InMemoryCollection()
        return self._collections[name]


try:
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.DATABASE_NAME]
except Exception:
    client = None
    db = InMemoryDatabase()


async def ping_database() -> bool:
    if client is None:
        return False
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False
