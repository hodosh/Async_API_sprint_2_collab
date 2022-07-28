import os
from logging import config as logging_config

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

# Настройки Redis
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# Настройки Elasticsearch
ES_HOST = os.getenv('ES_HOST', '127.0.0.1')
ES_PORT = int(os.getenv('ES_PORT', 9200))

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Индексы (необходимо уметь задавать для тестов)
MOVIES_INDEX = os.getenv('MOVIES_INDEX', 'movies')
GENRES_INDEX = os.getenv('GENRES_INDEX', 'genres')
PERSONS_INDEX = os.getenv('PERSONS_INDEX', 'persons')

JAEGER_HOST = os.getenv('JAEGER_HOST', '127.0.0.1')
JAEGER_PORT = os.getenv('JAEGER_PORT', 6831)
