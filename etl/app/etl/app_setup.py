import os
import sys
import requests
import json
import pathlib

from setup_logging import *
from dotenv import load_dotenv

load_dotenv()
logger = setup_applevel_logger()

HOST = os.environ.get('ES_HOST', '127.0.0.1')
PORT = os.environ.get('ES_PORT', 9200)
ES_URL = f"http://{str(HOST)}:{PORT}/movies"

ES_INDEXES = {
    'movies': 'movies_es_schema_v2.json',
    'genres': 'genres_es_schema.json',
    'person': 'person_es_schema.json'
}
print(ES_INDEXES)

headers = {
    'Content-type': 'application/x-ndjson',
}

for es_index in ES_INDEXES:
    json_file_name = ES_INDEXES[es_index]
    print (json_file_name)
    #ogger.info(json_file_name)
    json_name = pathlib.Path(sys.argv[0]).parent / pathlib.Path(f"init/{json_file_name}")

    f = open(json_name)
    query = json.load(f)
    response = requests.put(ES_URL, headers=headers, data=query)

    logger.info("Elasticsearch initialisation results")
    logger.info(response.content)
