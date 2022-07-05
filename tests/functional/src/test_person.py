import elasticsearch
import pytest
from http import HTTPStatus

from constants import PERSONS_INDEX_NAME, MOVIES_INDEX_NAME
from testdata.persons import data
from testdata.redis_data import person_data
from utils.prepare import pre_tests_actions

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


class TestPerson:
    @classmethod
    def setup_class(cls):
        # метод, в котором можно определить действия ДО выполнения тестов данного класса
        # например, тут будут создаваться тестовый индекс и загружаться общие для всех тестов тестовые данные
        pre_tests_actions()

    async def test_get_person_by_id_success(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(PERSONS_INDEX_NAME, data.base_person_data)
        # Выполнение запроса
        person_id = data.base_person_data['id']
        response = await make_get_request(f'/persons/{person_id}')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        assert response.body

        assert response.body == data.base_person_data

    async def test_get_not_existing_person_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request(f'/persons/FAKE')

        # Проверка результата
        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == {'detail': 'Person not found'}

    async def test_person_search_base_success(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(PERSONS_INDEX_NAME, data.person_list_data)
        # Выполнение запроса
        response = await make_get_request(f'/persons/')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        # Проверяем, что возвращается список персон
        assert isinstance(response.body, list)
        assert len(response.body) > 0
        # Проверяем ключи возвращенных персон
        assert response.body[0].keys() == data.person_list_data[0].keys()

    async def test_person_search_pagination_success(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(PERSONS_INDEX_NAME, data.person_list_data)
        # Выполнение запроса
        response = await make_get_request('/persons/?page_size=5&page_number=1')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        assert len(response.body) == 5

    async def test_person_search_pagination_wrong_page_fail(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(PERSONS_INDEX_NAME, data.person_list_data)
        # Выполнение запроса
        response = await make_get_request('/persons/?page_size=5&page_number=100')

        # Проверка результата
        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == {'detail': 'Person not found'}

    async def test_person_search_pagination_wrong_condition_fail(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(PERSONS_INDEX_NAME, data.person_list_data)
        # Выполнение запроса
        response = await make_get_request('/persons/?page_size=AAAA&page_number=100')

        # Проверка результата
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.body == {'detail': [{
            'loc': ['query', 'page_size'],
            'msg': 'value is not a valid integer',
            'type': 'type_error.integer',
        }]}

    async def test_person_search_by_empty_query_success(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/persons/search')

        # Проверка результата
        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == {'detail': 'Person not found'}

    async def test_person_search_query_required_field_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/persons/search/?')

        # Проверка результата
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.body == {'detail': [{
            'loc': ['query', 'query'],
            'msg': 'field required',
            'type': 'value_error.missing',
        }]}

    async def test_persons_search_by_query_success(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(PERSONS_INDEX_NAME, data.person_list_data)
        keyword = data.person_list_data[0]['full_name'].split(' ')[0]
        # Выполнение запроса
        response = await make_get_request(f'/persons/search/?query={keyword}')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        items = response.body
        # Проверяем, что возвращается список персон
        assert isinstance(items, list)
        assert len(items) > 0
        # Проверяем ключи возвращенных персон
        assert items[0].keys() == data.person_list_data[0].keys()
        # Проверяем, что во всех ответах есть значение из запроса
        assert len(items) == len([item for item in items if keyword in item['full_name']])

    async def test_person_search_by_query_fail(self, make_get_request):
        # Выполнение запроса
        response = await make_get_request('/persons/search/?query=_+-*')

        # Проверка результата
        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == {'detail': 'Person not found'}

    async def test_person_get_details_success(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(MOVIES_INDEX_NAME, data.film_data)
        await data_loader(PERSONS_INDEX_NAME, data.person_detailed_info_data)
        person_id = data.person_detailed_info_data['id']
        # Выполнение запроса
        response = await make_get_request(f'/persons/{person_id}/film/')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        assert response.body == [
            {
                'id': data.film_data['id'],
                'imdb_rating': data.film_data['imdb_rating'],
                'title': data.film_data['title'],
            },
        ]

    async def test_person_get_details_fail(self, make_get_request, data_loader):
        # загружаем данные
        await data_loader(PERSONS_INDEX_NAME, data.person_detailed_fail_data)
        person_id = data.person_detailed_fail_data['id']
        # Выполнение запроса
        response = await make_get_request(f'/persons/{person_id}/film/')
        # Проверка результата
        assert response.status == HTTPStatus.NOT_FOUND
        assert response.body == {'detail': 'film not found'}

    async def test_get_person_by_id_from_cache(self, make_get_request, put_to_redis, es_client):
        # кладем напрямую в редис данные, которых нет в эластике
        await put_to_redis(**person_data)
        person_id = person_data['key']
        response = await make_get_request(f'/persons/{person_id}')

        # Проверка результата
        assert response.status == HTTPStatus.OK
        assert response.body['id'] == person_id

        # проверим, что данных нет в эластике
        with pytest.raises(elasticsearch.exceptions.NotFoundError) as e:
            await es_client.get(index=PERSONS_INDEX_NAME, id=person_id)
        assert e.value.args[0] == HTTPStatus.NOT_FOUND
