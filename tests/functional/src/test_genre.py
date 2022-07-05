import elasticsearch
import pytest
from http import HTTPStatus

from constants import GENRES_INDEX_NAME, MOVIES_INDEX_NAME
from testdata.genres import data
from testdata.redis_data import genre_data
from utils.prepare import pre_tests_actions

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


class TestGenre:
    @classmethod
    def setup_class(cls):
        # метод, в котором можно определить действия ДО выполнения тестов данного класса
        # например, тут будут создаваться тестовый индекс и загружаться общие для всех тестов тестовые данные
        pre_tests_actions()

    async def test_get_genre_by_id_success(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(GENRES_INDEX_NAME, data.base_genre_data)
        # Выполнение запроса
        genre_id = data.base_genre_data['id']
        response = await make_get_request(f'/genres/{genre_id}')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        assert response.body

        assert response.body == {
            'id': genre_id,
            'description': data.base_genre_data['description'],
            'name': data.base_genre_data['name'],
        }

    async def test_get_not_existing_genre_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request(f'/genres/FAKE')

        # Проверка результата
        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == {'detail': 'Genre not found'}

    async def test_get_genres_list_success(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(GENRES_INDEX_NAME, data.base_genre_data)
        # Выполнение запроса
        response = await make_get_request(f'/genres/')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        assert isinstance(response.body, list)
        assert list(response.body[0].keys()) == ['id', 'name']

    async def test_genre_get_film_details_success(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(MOVIES_INDEX_NAME, data.film_data)
        await data_loader(GENRES_INDEX_NAME, data.genre_with_film_details)
        genre_id = data.genre_with_film_details['id']
        # Выполнение запроса
        response = await make_get_request(f'/genres/{genre_id}/film/')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        assert response.body == [
            {
                'id': data.film_data['id'],
                'title': data.film_data['title'],
                'imdb_rating': data.film_data['imdb_rating'],
            },
        ]

    async def test_genre_get_film_details_fail(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(GENRES_INDEX_NAME, data.genre_without_film_details)
        genre_id = data.genre_without_film_details['id']
        # Выполнение запроса
        response = await make_get_request(f'/genres/{genre_id}/film/')

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
