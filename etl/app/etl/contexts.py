import logging
from contextlib import contextmanager

import backoff
import redis
import requests
from elasticsearch import Elasticsearch, ElasticsearchException


def backoff_handler(details):
    logging.warning("Elasticsearch - Backing off {wait:0.1f} seconds after {tries} tries ".format(**details))


@backoff.on_exception(backoff.expo, (requests.HTTPError, requests.ConnectionError), on_backoff=backoff_handler)
@contextmanager
def es_context(**kwargs):
    es = Elasticsearch(**kwargs)
    try:
        yield es
    except ElasticsearchException as er:
        logging.exception(er)
    finally:
        es.close()


@contextmanager
@backoff.on_exception(backoff.expo, redis.RedisError, on_backoff=backoff_handler)
def redis_context(**kwargs):
    _redis = redis.Redis(**kwargs)
    try:
        yield _redis
    except redis.RedisError as err:
        logging.exception(err)
