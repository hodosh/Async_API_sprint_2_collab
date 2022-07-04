from typing import List

from aioredis import Redis
import orjson

from models.models import ORJSONModel
from utils.common import backoff

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class RedisService:
    def __init__(self, redis: Redis, model: ORJSONModel):
        self.redis = redis
        self.model = model

    @backoff()
    async def set(self, key: str, item: ORJSONModel):
        item_dump = item.json()
        await self.redis.set(key, item_dump, expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    @backoff()
    async def get(self, key: str):
        item_dump = await self.redis.get(key)
        if not item_dump:
            return None

        return orjson.loads(item_dump)

    @backoff()
    async def set_list(self, key: str, items: List[ORJSONModel]):
        items_dump = [item.json() for item in items]
        items_dump = orjson.dumps(items_dump)
        await self.redis.set(str(key), items_dump, expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    @backoff()
    async def get_list(self, key: str):
        item_dump = await self.redis.get(str(key))
        if not item_dump:
            return None
        items_json = orjson.loads(item_dump)
        items_obj = [orjson.loads(item) for item in items_json]

        return items_obj
