from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from core.config import MOVIES_INDEX, GENRES_INDEX, PERSONS_INDEX
from db.elastic import get_elastic
from db.redis import get_redis
from models.models import Person, Genre, Film
from services.movie_service import MovieService
from db.async_cache_storage import AsyncCacheStorage
from db.async_fulltext_search import FullTextSearch


@lru_cache()
def get_film_service(
        redis: AsyncCacheStorage = Depends(get_redis),
        elastic: FullTextSearch = Depends(get_elastic),
) -> MovieService:
    return MovieService(redis, elastic, MOVIES_INDEX, Film)


@lru_cache()
def get_genre_service(
        redis: AsyncCacheStorage = Depends(get_redis),
        elastic: FullTextSearch = Depends(get_elastic),
) -> MovieService:
    return MovieService(redis, elastic, GENRES_INDEX, Genre)


@lru_cache()
def get_person_service(
        redis: AsyncCacheStorage = Depends(get_redis),
        elastic: FullTextSearch = Depends(get_elastic),
) -> MovieService:
    return MovieService(redis, elastic, PERSONS_INDEX, Person)
