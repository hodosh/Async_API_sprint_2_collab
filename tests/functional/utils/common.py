import time
from functools import wraps
from urllib.parse import urljoin

from elasticsearch import Elasticsearch
from requests import Session as _Session
import logging

from conftest import work_dir
from settings import settings


def prepare_es_actions(file_name: str):
    """
    Метод для работы с тестовыми данными в Elasticsearch
    @param file_name: имя файла, где описаны данные и действия, которые с ними надо выполнить
    """
    with Elasticsearch(hosts=f'{settings.es_host.rstrip("/")}:{settings.es_port}') as client:
        with open(work_dir().parent / 'testdata' / file_name, 'r') as f:
            data = f.read()
        client.bulk(data)


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10, logger=logging.getLogger('backoff')):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param logger: логгер, куда должен писаться статус выполнения функции
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            n = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    sleep_time = start_sleep_time * factor ** n
                    logger.warn(f'sleep_time: {sleep_time}, border_sleep_time: {border_sleep_time}')
                    if sleep_time >= border_sleep_time:
                        raise e
                    time.sleep(sleep_time)
                    n += 1

        return inner

    return func_wrapper


class Session(_Session):
    def __init__(self, api_url):
        super(Session, self).__init__()
        self.api_url = api_url

    def request(self, method, url, *args, convert_response=True, **kwargs):
        """
        Метод сразу возвращает результат в виде словаря и вызывает исключение при ошибке
        """
        url = urljoin(self.api_url, url.lstrip('/'))
        response = super(Session, self).request(method, url, *args, **kwargs)
        response.raise_for_status()
        return response.json() if convert_response else response
