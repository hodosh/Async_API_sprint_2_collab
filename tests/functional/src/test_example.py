import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock
import requests

import pytest


def test_simple():
    assert 1 + 1 == 2


def test_zero_division_error():
    # так проверяем исключения
    with pytest.raises(ZeroDivisionError) as e:
        1 / 0

    assert e.value.args[0] == 'division by zero'


@patch('requests.get')
def test_side_effect(get_mock: MagicMock):
    # side_effect подменяет вызываемую функцию,
    # можно вызвать/написать внешнюю функцию
    get_mock.side_effect = lambda x: 'some result'
    resp = requests.get('mock_url')

    assert resp == 'some result'
    assert get_mock.called


@patch('requests.get')
def test_return_value(get_mock: MagicMock):
    # return_value подменяет возвращаемый результат
    get_mock.return_value = 'some result'
    resp = requests.get('mock_url')

    assert resp == 'some result'
    assert get_mock.called


async def count():
    return 1


@pytest.mark.asyncio
async def test_async():
    result = [await asyncio.gather(count(), count(), count())]
    assert result == [[1, 1, 1]]


def test_fixture(work_dir):
    # фикстуры не импортируются, а пробрасываются атрибутом метода
    assert work_dir == Path().absolute()
