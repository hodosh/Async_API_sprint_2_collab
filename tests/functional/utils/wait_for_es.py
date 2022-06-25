from tests.functional import logger
from tests.functional.settings import settings
from tests.functional.utils.common import Session, backoff


class ElasticsearchWaiter:
    def __init__(self):
        self.session = Session(settings.es_host)

    @backoff(border_sleep_time=30)
    def wait_for_service_availability(self):
        return self.session.get(url='')


if __name__ == '__main__':
    logger.info('Waiting for ElasticSearch availability')
    es_waiter = ElasticsearchWaiter()
    es_waiter.wait_for_service_availability()
    logger.info('ElasticSearch is ready!')
