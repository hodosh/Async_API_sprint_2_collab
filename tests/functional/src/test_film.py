import pytest

from testdata.movies import results
from utils.prepare import pre_tests_actions, post_tests_actions


class TestFilm:
    @classmethod
    def setup_class(cls):
        # метод, в котором можно определить действия ДО выполнения тестов данного класса
        # например, тут будут создаваться тестовый индекс и загружаться общие для всех тестов тестовые данные
        pre_tests_actions(schema_name='test_movies',
                          data_path_name='movies')

    @classmethod
    def teardown_class(cls):
        # метод, в котором можно определить действия ПОСЛЕ выполнения тестов данного класса
        # например, тут будут удаляться общие для всех тестов тестовые данные (чистим за собой мусор)
        post_tests_actions(data_path_name='movies')

    @pytest.mark.asyncio
    async def test_get_film_by_id(self, es_client, make_get_request):
        # Выполнение запроса
        film_id = '111111-111111-111111-111111'
        response = await make_get_request(f'/films/{film_id}')

        # Проверка результата
        assert response.status == 200
        assert len(response.body) == 8

        assert response.body == results.film_by_id_result

    @pytest.mark.asyncio
    async def test_get_not_existing_film(self, es_client, make_get_request):
        # Выполнение запроса
        response = await make_get_request(f'/films/FAKE')

        # Проверка результата
        assert response.status == 404
        assert response.body == {'detail': 'film not found'}

    @pytest.mark.asyncio
    async def test_film_search_base(self, es_client, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/films/')

        # Проверка результата
        assert response.status == 200
        # Проверяем, что возвращается список фильмов
        assert isinstance(response.body['items'], list)
        assert len(response.body['items']) > 0
        # Проверяем ключи возвращенных фильмов
        assert list(response.body['items'][0].keys()) == ['uuid', 'title', 'imdb_rating']

