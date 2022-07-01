import json
import os
import pathlib
import sys

from dotenv import load_dotenv

from contexts import es_context, redis_context
from setup_logging import setup_applevel_logger

load_dotenv()
logger = setup_applevel_logger()
DEBUG = os.environ.get('DEBUG', False) == 'True'

REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

ES_HOST = os.environ.get('ES_HOST', '127.0.0.1')
ES_PORT = os.environ.get('ES_PORT', 9200)
# ES_URL = f"http://{str(HOST)}:{PORT}/movies"

ES_INDEXES = {
    'movies': 'movies_es_schema.json',
    'genres': 'genres_es_schema.json',
    'persons': 'person_es_schema.json'
}


def setup():
    with es_context(hosts=[{'host': ES_HOST, 'port': ES_PORT}]) as es, redis_context(
            host=REDIS_HOST, port=REDIS_PORT) as redis:
        if DEBUG:
            redis.flushdb()

        for es_index in ES_INDEXES:
            json_file_name = ES_INDEXES[es_index]
            json_name = pathlib.Path(sys.argv[0]).parent / pathlib.Path(f"init/{json_file_name}")

            with open(json_name) as es_schema:
                settings, mappings = json.loads(es_schema.read()).values()
            if DEBUG:
                if es.indices.exists(index=es_index):
                    es.indices.delete(index=es_index)
                    logger.debug(f"Elasticsearch index {es_index} is removed.")
            if not es.indices.exists(index=es_index):
                es.indices.create(index=es_index, settings=settings, mappings=mappings)
                logger.info(f"Elasticsearch {es_index}-index successfully created.")


if __name__ == '__main__':
    logger.info('App setup indices.')
    setup()
