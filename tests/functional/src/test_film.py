import json

import pytest
from elasticsearch import Elasticsearch

import testdata.films as test_data
from settings import settings
import testdata.results.films as results


class TestFilm:
    @classmethod
    def setup_class(cls):
        # метод, в котором можно определить действия ДО выполнения тестов данного класса
        # например, тут будут загружаться общие для всех тестов тестовые данные
        # PS не работает асинхронно, поэтому такая конструкция
        data = ''
        with Elasticsearch(hosts=f'{settings.es_host.rstrip("/")}:{settings.es_port}') as client:
            for film in test_data.es_films_list:
                film_id = film.get('id')
                data += f'{{ "index" : {{ "_index" : "movies", "_id" : "{film_id}" }} }}\n{json.dumps(film)}\n'
            client.bulk(data)

    @classmethod
    def teardown_class(cls):
        # метод, в котором можно определить действия ПОСЛЕ выполнения тестов данного класса
        # например, тут будут удаляться общие для всех тестов тестовые данные (чистим за собой мусор)
        # PS не работает асинхронно, поэтому такая конструкция
        data = ''
        with Elasticsearch(hosts=f'{settings.es_host.rstrip("/")}:{settings.es_port}') as client:
            for film in test_data.es_films_list:
                film_id = film.get('id')
                data += f'{{ "delete" : {{ "_index" : "movies", "_id" : "{film_id}" }} }}\n'
            client.bulk(data)

    @pytest.mark.asyncio
    async def test_get_film_by_id(self, es_client, make_get_request):
        # Выполнение запроса
        film = test_data.es_films_list[0]
        film_id = film.get('id')
        response = await make_get_request(f'/films/{film_id}')

        # Проверка результата
        assert response.status == 200
        assert len(response.body) == 8

        assert response.body == results.film_by_id_result
