from redis import Redis

from settings import settings
from utils import logger
from utils.common import backoff


class RedisWaiter:
    def __init__(self):
        self.redis = Redis(host=settings.redis_host, port=settings.redis_port, socket_connect_timeout=1)

    @backoff(border_sleep_time=10)
    def wait_for_service_availability(self):
        return self.redis.ping()


if __name__ == '__main__':
    logger.info('Waiting for Redis availability')
    redis_waiter = RedisWaiter()
    redis_waiter.wait_for_service_availability()
    logger.info('Redis is ready!')
