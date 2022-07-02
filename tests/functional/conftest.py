import asyncio
from pathlib import Path
import typing as t
from dataclasses import dataclass
from multidict import CIMultiDictProxy

from elasticsearch import AsyncElasticsearch
import pytest
import aiohttp
import aioredis

from settings import settings


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=f'{settings.es_host.rstrip("/")}:{settings.es_port}')
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: t.Optional[dict] = None) -> HTTPResponse:
        params = params or {}
        url = f'{settings.api_host.rstrip("/")}:{settings.api_port}/api/v1{method}'
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture(scope='session')
def tmp_path_session(request, tmp_path_factory):
    from _pytest.tmpdir import _mk_tmp

    yield _mk_tmp(request, tmp_path_factory)


@pytest.fixture(scope='function')
def read_from_file():
    def _read_from_file(filepath: t.Union[str, Path]):
        with open(filepath, 'r') as f:
            return f.read()

    return _read_from_file


@pytest.fixture(scope='function')
def copy_lst_files(work_dir):
    def _copy_lst_files(files_list: t.Iterable[Path], to: Path = work_dir):
        for file in files_list:
            (to / file.name).write_text(
                (work_dir / file).read_text(encoding='utf-8'),
            )

    return _copy_lst_files


@pytest.fixture(scope='function')
def put_to_redis():
    async def inner(key: t.Union[str, bytes], data: t.Union[str, bytes]):
        redis = await aioredis.create_redis_pool((settings.redis_host, settings.redis_port), minsize=10, maxsize=20)
        await redis.set(key, data, expire=60)

    return inner
