from functools import lru_cache
from typing import Optional

import pickle
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.models import Film
from models.models import ORJSONModel


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class RedisService:
    def __init__(self, redis: Redis, model: ORJSONModel):
        self.redis = redis
        self.model = model

    async def set(self, key: str, item: ORJSONModel):
        key_pickled = pickle.dumps(key, 0).decode()
        pickled_item = pickle.dumps(item, 0).decode()
        await self.redis.set(key_pickled, pickled_item, expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def get(self, key: str):
        key_pickled = pickle.dumps(key, 0).decode()
        pickled_item = await self.redis.get(key_pickled)
        if not pickled_item:
            return None

        return pickle.loads(pickled_item)
