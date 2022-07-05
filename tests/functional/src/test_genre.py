import elasticsearch
import pytest
from http import HTTPStatus

from constants import GENRES_DATA_PATH_NAME, GENRES_INDEX_NAME
from testdata.genres import results
from testdata.redis_data import genre_data
from utils.prepare import pre_tests_actions, post_tests_actions

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


class TestGenre:
    @classmethod
    def setup_class(cls):
        # метод, в котором можно определить действия ДО выполнения тестов данного класса
        # например, тут будут создаваться тестовый индекс и загружаться общие для всех тестов тестовые данные
        pre_tests_actions(data_path_name=GENRES_DATA_PATH_NAME)

    @classmethod
    def teardown_class(cls):
        # метод, в котором можно определить действия ПОСЛЕ выполнения тестов данного класса
        # например, тут будут удаляться общие для всех тестов тестовые данные (чистим за собой мусор)
        post_tests_actions(data_path_name=GENRES_DATA_PATH_NAME)

    async def test_get_genre_by_id_success(self, make_get_request):
        # Выполнение запроса
        genre_id = '333333-000000-000000-000000'
        response = await make_get_request(f'/genres/{genre_id}')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        assert response.body

        assert response.body == results.genre_by_id_result

    async def test_get_not_existing_genre_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request(f'/genres/FAKE')

        # Проверка результата
        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == {'detail': 'Genre not found'}

    async def test_get_genres_list_success(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request(f'/genres/')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        assert isinstance(response.body, list)
        assert list(response.body[0].keys()) == ['id', 'name']

    async def test_genre_get_film_details_success(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/genres/333333-000000-000000-000001/film/')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        assert response.body == results.genre_detailed_result

    async def test_genre_get_film_details_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/genres/333333-000000-000000-000002/film/')

        # Проверка результата
        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == {'detail': 'film not found'}

    async def test_get_genre_by_id_from_cache(self, make_get_request, put_to_redis, es_client):
        # кладем напрямую в редис данные, которых нет в эластике
        await put_to_redis(**genre_data)
        genre_id = genre_data['key']
        response = await make_get_request(f'/genres/{genre_id}')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        assert response.body['id'] == genre_id

        # проверим, что данных нет в эластике
        with pytest.raises(elasticsearch.exceptions.NotFoundError) as e:
            await es_client.get(index=GENRES_INDEX_NAME, id=genre_id)
        assert e.value.args[0] == HTTPStatus.NOT_FOUND
