import os
from logging import config as logging_config

from pydantic import BaseSettings, Field

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    # Название проекта. Используется в Swagger-документации
    PROJECT_NAME = Field(env='PROJECT_NAME', default='movies')

    # Настройки Redis
    REDIS_HOST = Field(env='REDIS_HOST', default='127.0.0.1')
    REDIS_PORT = Field(env='REDIS_PORT', default=6379)

    # Настройки Elasticsearch
    ES_HOST = Field(env='ES_HOST', default='127.0.0.1')
    ES_PORT = Field(env='ES_PORT', default=9200)

    # Корень проекта
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Индексы (необходимо уметь задавать для тестов)
    MOVIES_INDEX = Field(env='MOVIES_INDEX', default='movies')
    GENRES_INDEX = Field(env='GENRES_INDEX', default='genres')
    PERSONS_INDEX = Field(env='PERSONS_INDEX', default='persons')

    AUTH_API_HOST = Field(env='AUTH_API_HOST', default='127.0.0.1')
    AUTH_API_PORT = Field(env='AUTH_API_PORT', default=5000)
    AUTH_API_CHECK_TOKEN_ENDPOINT = Field(env='AUTH_API_CHECK_TOKEN_ENDPOINT', default='/api/v1/users/check_access')


settings = Settings()
