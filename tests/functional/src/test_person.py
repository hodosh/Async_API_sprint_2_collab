import pytest

from testdata.persons import results
from utils.prepare import pre_tests_actions, post_tests_actions

INDEX_NAME = 'test_persons'
DATA_PATH_NAME = 'persons'


class TestPerson:
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
    async def test_get_person_by_id_success(self, make_get_request):
        # Выполнение запроса
        person_id = '222222-000000-000000-000000'
        response = await make_get_request(f'/persons/{person_id}')

        # Проверка результата
        assert response.status == 200
        assert response.body

        assert response.body == results.person_by_id_result
