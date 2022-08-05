from functools import lru_cache

from fastapi import Depends

from core.config import settings
from db.async_cache_storage import AsyncCacheStorage
from db.async_fulltext_search import FullTextSearch
from db.elastic import get_elastic
from db.redis import get_redis
from models.models import Person, Genre, Film
from services.movie_service import MovieService


@lru_cache()
def get_film_service(
        redis: AsyncCacheStorage = Depends(get_redis),
        elastic: FullTextSearch = Depends(get_elastic),
) -> MovieService:
    return MovieService(redis, elastic, settings.MOVIES_INDEX, Film)


@lru_cache()
def get_genre_service(
        redis: AsyncCacheStorage = Depends(get_redis),
        elastic: FullTextSearch = Depends(get_elastic),
) -> MovieService:
    return MovieService(redis, elastic, settings.GENRES_INDEX, Genre)


@lru_cache()
def get_person_service(
        redis: AsyncCacheStorage = Depends(get_redis),
        elastic: FullTextSearch = Depends(get_elastic),
) -> MovieService:
    return MovieService(redis, elastic, settings.PERSONS_INDEX, Person)
