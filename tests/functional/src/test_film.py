import elasticsearch
import pytest
from http import HTTPStatus

from constants import MOVIES_INDEX_NAME
from testdata.movies import data
from testdata.redis_data import film_data
from utils.prepare import pre_tests_actions

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


class TestFilm:
    @classmethod
    def setup_class(cls):
        # метод, в котором можно определить действия ДО выполнения тестов данного класса
        # например, тут сначала удаляются тестовые индексы и сразу создаются заново
        pre_tests_actions()

    async def test_get_film_by_id_success(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(MOVIES_INDEX_NAME, data.base_film_data)
        film_id = data.base_film_data['id']
        # Выполнение запроса
        response = await make_get_request(f'/films/{film_id}')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        assert len(response.body) == 8

        assert response.body == data.base_film_data

    async def test_get_not_existing_film_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request(f'/films/FAKE')

        # Проверка результата
        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == {'detail': 'film not found'}

    async def test_film_search_base_success(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(MOVIES_INDEX_NAME, data.base_film_data)
        # Выполнение запроса
        response = await make_get_request('/films/')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        # Проверяем, что возвращается список фильмов
        assert isinstance(response.body, list)
        assert len(response.body) > 0
        # Проверяем ключи возвращенных фильмов
        assert response.body[0].keys() == data.base_film_data.keys()

    async def test_film_search_sort_by_imdb_rating_success(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(MOVIES_INDEX_NAME, data.film_list_data)
        # Выполнение запроса
        response = await make_get_request('/films/?sort=-imdb_rating')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        rating_list = [item['imdb_rating'] for item in response.body]
        assert rating_list == sorted(rating_list, reverse=True)

    async def test_film_search_filter_by_genre_success(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(MOVIES_INDEX_NAME, data.base_film_data)
        genre_id = data.base_film_data['genres'][0]['id']
        # Выполнение запроса
        response = await make_get_request(f'/films/?filter_genre={genre_id}')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        assert len(response.body) == 1
        assert response.body.pop()['genres'] == data.base_film_data['genres']

    async def test_film_search_filter_by_genre_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/?filter_genre=FAKE')

        # Проверка результата
        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == {'detail': 'film not found'}

    async def test_film_search_by_empty_query_success(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/search')

        # Проверка результата (query обязателен)
        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == {'detail': 'film not found'}

    async def test_film_search_query_required_field_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/search/?')

        # Проверка результата
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.body == {'detail': [{
            'loc': ['query', 'query'],
            'msg': 'field required',
            'type': 'value_error.missing',
        }]}

    async def test_film_search_by_query_success(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(MOVIES_INDEX_NAME, data.base_film_data)
        # Выполнение запроса
        keyword = data.base_film_data['title'].split(' ')[0]
        response = await make_get_request(f'/films/search/?query={keyword}')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        items = response.body
        # Проверяем, что возвращается список фильмов
        assert isinstance(items, list)
        assert len(items) > 0
        # Проверяем ключи возвращенных фильмов
        assert response.body[0].keys() == data.base_film_data.keys()

        # Проверяем, что во всех ответах есть значение из запроса
        assert len(items) == len([item for item in items if keyword in item['title']])

    async def test_film_search_by_query_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/search/?query=_+-*')

        # Проверка результата
        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == {'detail': 'film not found'}

    async def test_film_search_pagination_success(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(MOVIES_INDEX_NAME, data.film_list_data)
        # Выполнение запроса
        keyword = data.film_list_data[0]['title'][0:4]  # просто берем общий префикс
        response = await make_get_request(f'/films/search/?query={keyword}&page_size=5&page_number=1')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        assert len(response.body) == 5
        assert all([keyword in item['title'] for item in response.body])

    async def test_film_search_pagination_wrong_page_fail(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(MOVIES_INDEX_NAME, data.film_list_data)
        # Выполнение запроса
        keyword = data.film_list_data[0]['title'][0:4]  # просто берем общий префикс
        # Выполнение запроса
        response = await make_get_request(f'/films/search/?query={keyword}&page_size=5&page_number=100')

        # Проверка результата
        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == {'detail': 'film not found'}

    async def test_film_search_pagination_wrong_condition_fail(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(MOVIES_INDEX_NAME, data.film_list_data)
        # Выполнение запроса
        keyword = data.film_list_data[0]['title'][0:4]  # просто берем общий префикс
        # Выполнение запроса
        response = await make_get_request(f'/films/search/?query={keyword}&page_size=AAAA&page_number=100')

        # Проверка результата
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.body == {'detail': [{
            'loc': ['query', 'page_size'],
            'msg': 'value is not a valid integer',
            'type': 'type_error.integer',
        }]}

    async def test_get_film_by_id_from_cache(self, make_get_request, put_to_redis, es_client):
        # кладем напрямую в редис данные, которых нет в эластике
        await put_to_redis(**film_data)
        film_uuid = film_data['key']
        response = await make_get_request(f'/films/{film_uuid}')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        assert response.body['id'] == film_uuid

        # проверим, что данных нет в эластике
        with pytest.raises(elasticsearch.exceptions.NotFoundError) as e:
            await es_client.get(index=MOVIES_INDEX_NAME, id=film_uuid)
        assert e.value.args[0] == HTTPStatus.NOT_FOUND
