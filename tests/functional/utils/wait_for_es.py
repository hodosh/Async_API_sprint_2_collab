from settings import settings
from utils import logger
from utils.common import Session, backoff


class ElasticsearchWaiter:
    def __init__(self):
        self.session = Session(f'{settings.es_host.rstrip("/")}:{settings.es_port}')

    @backoff(border_sleep_time=10)
    def wait_for_service_availability(self):
        return self.session.get(url='')


if __name__ == '__main__':
    logger.info('Waiting for ElasticSearch availability')
    es_waiter = ElasticsearchWaiter()
    es_waiter.wait_for_service_availability()
    logger.info('ElasticSearch is ready!')
