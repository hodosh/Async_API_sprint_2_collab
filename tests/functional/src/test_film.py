import pytest

from testdata.movies import results
from testdata.movies.redis_data import cache_data
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
        post_tests_actions(index_name=INDEX_NAME, data_path_name=DATA_PATH_NAME)

    @pytest.mark.asyncio
    async def test_get_film_by_id_success(self, es_client, make_get_request):
        # Выполнение запроса
        film_id = '111111-111111-111111-111111'
        response = await make_get_request(f'/films/{film_id}')

        # Проверка результата
        assert response.status == 200
        assert len(response.body) == 8

        assert response.body == results.film_by_id_result

    @pytest.mark.asyncio
    async def test_get_not_existing_film_fail(self, es_client, make_get_request):
        # Выполнение запроса
        response = await make_get_request(f'/films/FAKE')

        # Проверка результата
        assert response.status == 404
        assert response.body == {'detail': 'film not found'}

    @pytest.mark.asyncio
    async def test_film_search_base_success(self, es_client, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/')

        # Проверка результата
        assert response.status == 200
        # Проверяем, что возвращается список фильмов
        assert isinstance(response.body['items'], list)
        assert len(response.body['items']) > 0
        # Проверяем ключи возвращенных фильмов
        assert list(response.body['items'][0].keys()) == ['uuid', 'title', 'imdb_rating']

    @pytest.mark.asyncio
    async def test_film_search_by_empty_query_success(self, es_client, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/search')

        # Проверка результата
        assert response.status == 200
        # todo доделать тест

    @pytest.mark.asyncio
    async def test_film_search_by_query_success(self, es_client, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/search?query=Star')

        # Проверка результата
        assert response.status == 200
        items = response.body['items']
        # Проверяем, что возвращается список фильмов
        assert isinstance(items, list)
        assert len(items) > 0
        # Проверяем ключи возвращенных фильмов
        assert list(items[0].keys()) == ['uuid', 'title', 'imdb_rating']
        # Проверяем, что во всех ответах есть значение из запроса
        assert len(items) == len([item for item in items if 'Star' in item['title']])

    @pytest.mark.asyncio
    async def test_film_search_by_query_fail(self, es_client, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/search?query=_+-*')

        # Проверка результата
        assert response.status == 404
        assert response.body == {'detail': 'film not found'}

    @pytest.mark.asyncio
    async def test_film_search_by_multiple_query(self, es_client, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/search?query=Star&?query=Czars')

        # Проверка результата
        assert response.status == 200
        items = response.body['items']
        # Проверяем, что возвращается список фильмов
        assert isinstance(items, list)
        assert len(items) > 0
        # Проверяем ключи возвращенных фильмов
        assert list(items[0].keys()) == ['uuid', 'title', 'imdb_rating']
        # Проверяем, что во всех ответах есть значение из запроса
        assert len(items) == len([item for item in items if 'Star' in item['title'] and 'Czars' in item['title']])

    @pytest.mark.asyncio
    async def test_film_search_pagination(self, es_client, make_get_request):
        # todo сделать данные для пагинации
        # Выполнение запроса
        response = await make_get_request('/films/search?page=1&size=5')

        # Проверка результата
        assert response.status == 200
        assert len(response.body['page']) == 1
        assert len(response.body['size']) == 5
        assert len(response.body['items']) == 5

    @pytest.mark.asyncio
    async def test_get_film_by_id_from_cache(self, es_client, make_get_request, put_to_redis):
        # кладем напрямую в редис данные, которых нет в эластике
        put_to_redis(**cache_data)
        response = await make_get_request(f'/films/{cache_data["key"]}')

        # Проверка результата
        assert response.status == 200
        assert response.body['uuid'] == cache_data['key']
