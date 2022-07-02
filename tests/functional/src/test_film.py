import pytest

from testdata.movies import results
from testdata.redis_data import film_data
from utils.prepare import pre_tests_actions, post_tests_actions

INDEX_NAME = 'test_movies'
DATA_PATH_NAME = 'movies'


class TestFilm:
    @classmethod
    def setup_class(cls):
        # метод, в котором можно определить действия ДО выполнения тестов данного класса
        # например, тут будут создаваться тестовый индекс и загружаться общие для всех тестов тестовые данные
        pre_tests_actions(index_name=INDEX_NAME, data_path_name=DATA_PATH_NAME)

    @classmethod
    def teardown_class(cls):
        # метод, в котором можно определить действия ПОСЛЕ выполнения тестов данного класса
        # например, тут будут удаляться общие для всех тестов тестовые данные (чистим за собой мусор)
        # post_tests_actions(index_name=INDEX_NAME, data_path_name=DATA_PATH_NAME)
        pass

    @pytest.mark.asyncio
    async def test_get_film_by_id_success(self, make_get_request):
        # Выполнение запроса
        film_id = '111111-000000-000000-000000'
        response = await make_get_request(f'/films/{film_id}')

        # Проверка результата
        assert response.status == 200
        assert len(response.body) == 8

        assert response.body == results.film_by_id_result

    @pytest.mark.asyncio
    async def test_get_not_existing_film_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request(f'/films/FAKE')

        # Проверка результата
        assert response.status == 404
        assert response.body == {'detail': 'film not found'}

    @pytest.mark.asyncio
    async def test_film_search_base_success(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/')

        # Проверка результата
        assert response.status == 200
        # Проверяем, что возвращается список фильмов
        assert isinstance(response.body, list)
        assert len(response.body) > 0
        # Проверяем ключи возвращенных фильмов
        assert list(response.body[0].keys()) == ['id', 'title', 'imdb_rating']

    @pytest.mark.asyncio
    async def test_film_search_by_empty_query_success(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/search')

        # Проверка результата (query обязателен)
        assert response.status == 404
        assert response.body == {'detail': 'film not found'}

    @pytest.mark.asyncio
    async def test_film_search_query_required_field_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/search/?')

        # Проверка результата
        assert response.status == 422
        assert response.body == {'detail': [{
            'loc': ['query', 'query'],
            'msg': 'field required',
            'type': 'value_error.missing',
        }]}

    @pytest.mark.asyncio
    async def test_film_search_by_query_success(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/search/?query=Star')

        # Проверка результата
        assert response.status == 200
        items = response.body
        # Проверяем, что возвращается список фильмов
        assert isinstance(items, list)
        assert len(items) > 0
        # Проверяем ключи возвращенных фильмов
        assert list(items[0].keys()) == ['id', 'title', 'imdb_rating', 'description']
        # Проверяем, что во всех ответах есть значение из запроса
        assert len(items) == len([item for item in items if 'Star' in item['title']])

    @pytest.mark.asyncio
    async def test_film_search_by_query_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/search/?query=_+-*')

        # Проверка результата
        assert response.status == 404
        assert response.body == {'detail': 'film not found'}

    @pytest.mark.asyncio
    async def test_film_search_pagination_success(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/search/?query=page&page_size=5&page_number=1')

        # Проверка результата
        assert response.status == 200
        assert len(response.body) == 5
        assert all(['page' in item['title'] for item in response.body])

    @pytest.mark.asyncio
    async def test_film_search_pagination_wrong_page_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/search/?query=page&page_size=5&page_number=100')

        # Проверка результата
        assert response.status == 404
        assert response.body == {'detail': 'film not found'}

    @pytest.mark.asyncio
    async def test_film_search_pagination_wrong_condition_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/search/?query=page&page_size=AAAA&page_number=100')

        # Проверка результата
        assert response.status == 422
        assert response.body == {'detail': [{
            'loc': ['query', 'page_size'],
            'msg': 'value is not a valid integer',
            'type': 'type_error.integer',
        }]}

    @pytest.mark.asyncio
    async def test_get_film_by_id_from_cache(self, make_get_request, put_to_redis):
        # TODO доделать!
        # кладем напрямую в редис данные, которых нет в эластике
        put_to_redis(**film_data)
        film_uuid = film_data['key']
        response = await make_get_request(f'/films/{film_uuid}')

        # Проверка результата
        assert response.status == 200
        assert response.body['uuid'] == film_uuid
