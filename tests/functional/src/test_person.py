import elasticsearch
import pytest

from constants import PERSONS_DATA_PATH_NAME, PERSONS_INDEX_NAME
from testdata.persons import results
from testdata.redis_data import person_data
from utils.prepare import pre_tests_actions, post_tests_actions


class TestPerson:
    @classmethod
    def setup_class(cls):
        # метод, в котором можно определить действия ДО выполнения тестов данного класса
        # например, тут будут создаваться тестовый индекс и загружаться общие для всех тестов тестовые данные
        pre_tests_actions(data_path_name=PERSONS_DATA_PATH_NAME)

    @classmethod
    def teardown_class(cls):
        # метод, в котором можно определить действия ПОСЛЕ выполнения тестов данного класса
        # например, тут будут удаляться общие для всех тестов тестовые данные (чистим за собой мусор)
        post_tests_actions(data_path_name=PERSONS_DATA_PATH_NAME)

    @pytest.mark.asyncio
    async def test_get_person_by_id_success(self, make_get_request):
        # Выполнение запроса
        person_id = '222222-000000-000000-000000'
        response = await make_get_request(f'/persons/{person_id}')

        # Проверка результата
        assert response.status == 200
        assert response.body

        assert response.body == results.person_by_id_result

    @pytest.mark.asyncio
    async def test_get_not_existing_person_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request(f'/persons/FAKE')

        # Проверка результата
        assert response.status == 404
        assert response.body == {'detail': 'Person not found'}

    @pytest.mark.asyncio
    async def test_person_search_base_success(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request(f'/persons/')

        # Проверка результата
        assert response.status == 200
        # Проверяем, что возвращается список персон
        assert isinstance(response.body, list)
        assert len(response.body) > 0
        # Проверяем ключи возвращенных персон
        assert list(response.body[0].keys()) == ['id', 'full_name', 'film_roles']

    @pytest.mark.asyncio
    async def test_person_search_pagination_success(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/persons/?page_size=5&page_number=1')

        # Проверка результата
        assert response.status == 200
        assert len(response.body) == 5

    @pytest.mark.asyncio
    async def test_person_search_pagination_wrong_page_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/persons/?page_size=5&page_number=100')

        # Проверка результата
        assert response.status == 404
        assert response.body == {'detail': 'Person not found'}

    @pytest.mark.asyncio
    async def test_person_search_pagination_wrong_condition_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/persons/?page_size=AAAA&page_number=100')

        # Проверка результата
        assert response.status == 422
        assert response.body == {'detail': [{
            'loc': ['query', 'page_size'],
            'msg': 'value is not a valid integer',
            'type': 'type_error.integer',
        }]}

    @pytest.mark.asyncio
    async def test_person_search_by_empty_query_success(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/persons/search')

        # Проверка результата
        assert response.status == 404
        assert response.body == {'detail': 'Person not found'}

    @pytest.mark.asyncio
    async def test_person_search_query_required_field_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/persons/search/?')

        # Проверка результата
        assert response.status == 422
        assert response.body == {'detail': [{
            'loc': ['query', 'query'],
            'msg': 'field required',
            'type': 'value_error.missing',
        }]}

    @pytest.mark.asyncio
    async def test_persons_search_by_query_success(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/persons/search/?query=person')

        # Проверка результата
        assert response.status == 200
        items = response.body
        # Проверяем, что возвращается список персон
        assert isinstance(items, list)
        assert len(items) > 0
        # Проверяем ключи возвращенных персон
        assert list(items[0].keys()) == ['id', 'full_name', 'film_roles']
        # Проверяем, что во всех ответах есть значение из запроса
        assert len(items) == len([item for item in items if 'person' in item['full_name']])

    @pytest.mark.asyncio
    async def test_person_search_by_query_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/persons/search/?query=_+-*')

        # Проверка результата
        assert response.status == 404
        assert response.body == {'detail': 'Person not found'}

    @pytest.mark.asyncio
    async def test_person_get_details_success(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/persons/222222-000000-000000-000011/film/')

        # Проверка результата
        assert response.status == 200
        assert response.body == results.person_detailed_info

    @pytest.mark.asyncio
    async def test_person_get_details_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/persons/222222-000000-000000-000012/film/')

        # Проверка результата
        assert response.status == 404
        assert response.body == {'detail': 'film not found'}

    @pytest.mark.asyncio
    async def test_get_person_by_id_from_cache(self, make_get_request, put_to_redis, es_client):
        # кладем напрямую в редис данные, которых нет в эластике
        await put_to_redis(**person_data)
        person_id = person_data['key']
        response = await make_get_request(f'/persons/{person_id}')

        # Проверка результата
        assert response.status == 200
        assert response.body['id'] == person_id

        # проверим, что данных нет в эластике
        with pytest.raises(elasticsearch.exceptions.NotFoundError) as e:
            await es_client.get(index=PERSONS_INDEX_NAME, id=person_id)
        assert e.value.args[0] == 404
