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
        # todo описать индекс в testdata/persons/schema.json
        # todo описать данные в testdata/persons/prepare_test_data.json
        pre_tests_actions(index_name=INDEX_NAME, data_path_name=DATA_PATH_NAME)

    @classmethod
    def teardown_class(cls):
        # метод, в котором можно определить действия ПОСЛЕ выполнения тестов данного класса
        # например, тут будут удаляться общие для всех тестов тестовые данные (чистим за собой мусор)
        # todo описать данные в testdata/persons/remove_test_data.json
        post_tests_actions(index_name=INDEX_NAME, data_path_name=DATA_PATH_NAME)

    @pytest.mark.asyncio
    async def test_get_person_by_id_success(self, es_client, make_get_request):
        # todo крупные результаты тестов лучше описывать тут testdata/persons/results.py
        pass
