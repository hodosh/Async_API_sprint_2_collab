import json
from pathlib import Path

import elasticsearch
from elasticsearch import Elasticsearch

from conftest import work_dir
from settings import settings


def pre_tests_actions(schema_name: str, data_path_name: str):
    data_path = work_dir().parent / 'testdata' / data_path_name
    with Elasticsearch(hosts=f'{settings.es_host.rstrip("/")}:{settings.es_port}') as client:
        _create_es_schema(schema_name=schema_name, schema_path=data_path / 'schema.json', client=client)
        _prepare_es_actions(file_path=data_path / 'prepare_test_data.json', client=client)


def post_tests_actions(data_path_name: str):
    data_path = work_dir().parent / 'testdata' / data_path_name
    with Elasticsearch(hosts=f'{settings.es_host.rstrip("/")}:{settings.es_port}') as client:
        _prepare_es_actions(file_path=data_path / 'remove_test_data.json', client=client)


def _prepare_es_actions(file_path: Path, client):
    """
    Метод для работы с тестовыми данными в Elasticsearch
    @param client: клиент ES
    @param file_path: пусть до файла, где описаны данные и действия, которые с ними надо выполнить
    """
    with open(file_path, 'r') as f:
        data = f.read()
    client.bulk(data)


def _create_es_schema(schema_name: str, schema_path: Path, client):
    with open(schema_path, 'r') as f:
        mapping = json.load(f)
        try:
            client.indices.create(index=schema_name, body=mapping)
        except elasticsearch.exceptions.RequestError as e:
            # схема существует, игнорируем
            if not e.status_code == 400 and 'resource_already_exists_exception' in e.error:
                raise
