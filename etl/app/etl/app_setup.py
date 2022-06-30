import json
import os
import pathlib

import requests
from dotenv import load_dotenv

from contexts import es_context, redis_context
from setup_logging import *

load_dotenv()
logger = setup_applevel_logger()
DEBUG = os.environ.get('DEBUG', False) == 'True'

REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

HOST = os.environ.get('ES_HOST', '127.0.0.1')
PORT = os.environ.get('ES_PORT', 9200)
# ES_URL = f"http://{str(HOST)}:{PORT}/movies"

ES_INDEXES = {
    'movies': 'movies_es_schema_v2.json',
    'genres': 'genres_es_schema.json',
    'persons': 'person_es_schema.json'
}
print(ES_INDEXES)


def setup():
    with es_context(hosts=[{'host': HOST, 'port': PORT}]) as es, redis_context(
            host=REDIS_HOST, port=REDIS_PORT) as redis:
        if DEBUG:
            redis.flushdb()

        for es_index in ES_INDEXES:
            json_file_name = ES_INDEXES[es_index]
            print(json_file_name)
            json_name = pathlib.Path(sys.argv[0]).parent / pathlib.Path(f"init/{json_file_name}")

            with open(json_name) as es_schema:
                settings, mappings = json.loads(es_schema.read()).values()

            if not es.indices.exists(index=es_index):
                es.indices.create(index=es_index, settings=settings, mappings=mappings)


            # f = open(json_name)
            # query = json.load(f)
            # response = requests.put(ES_URL, headers=headers, data=query)

            logger.info("Elasticsearch initialisation results")
            # logger.info(response.content)


if __name__ == '__main__':
    setup()
