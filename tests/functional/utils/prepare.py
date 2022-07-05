import json
from pathlib import Path
from time import sleep

import elasticsearch
from elasticsearch import Elasticsearch

from constants import INDEX_PATHNAME
from settings import settings


def work_dir() -> Path:
    return Path(__file__).parent.parent.resolve()


def pre_tests_actions():
    data_path = work_dir() / 'testdata'
    with Elasticsearch(hosts=f'{settings.es_host.rstrip("/")}:{settings.es_port}') as client:
        # remove all schemas
        for index_name in INDEX_PATHNAME.keys():
            try:
                client.indices.delete(index_name)
            except elasticsearch.exceptions.NotFoundError:
                pass
        # create all schemas
        for index_name, pathname in INDEX_PATHNAME.items():
            _create_es_schema(index_name=index_name, schema_path=data_path / pathname / 'schema.json', client=client)
    # sleep to wait data appearance
    sleep(2)


def _prepare_es_actions(file_path: Path, client):
    """
    Метод для работы с тестовыми данными в Elasticsearch
    @param client: клиент ES
    @param file_path: пусть до файла, где описаны данные и действия, которые с ними надо выполнить
    """
    with open(file_path, 'r') as f:
        data = f.read()
    result = client.bulk(data)
    if result['errors'] is True:
        raise RuntimeError(f'Something went wrong: {result}')


def _create_es_schema(index_name: str, schema_path: Path, client):
    with open(schema_path, 'r') as f:
        mapping = json.load(f)
        try:
            client.indices.create(index=index_name, body=mapping)
        except elasticsearch.exceptions.RequestError as e:
            # схема существует, игнорируем
            if not e.status_code == 400 and 'resource_already_exists_exception' in e.error:
                raise
