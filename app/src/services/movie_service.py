from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch

from db.elastic_query_builder import QueryBuilder
from db.elastic_service import ElasticService
from db.redis_service import RedisService
from models.models import ORJSONModel


class MovieService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, elastic_index: str, model: ORJSONModel):
        self.redis_service = redis
        self.elastic = elastic
        self.model = model
        self.es_index = elastic_index

        self.elastic_service = ElasticService(elastic, elastic_index, model)
        self.redis_service = RedisService(redis, model)

    async def get_by_id(self, item_id: str) -> Optional[ORJSONModel]:
        item = await self.redis_service.get(item_id)
        if not item:
            item = await self.elastic_service.get_by_id(item_id)
            if not item:
                return None

            await self.redis_service.set(item_id, item)

        return item

    async def get_by_query(self, query_body: str) -> Optional[list[ORJSONModel]]:
        items = await self.redis_service.get_list(query_body)
        if not items:
            items = await self.elastic_service.get_by_query(query_body)
            if not items:
                return None

            await self.redis_service.set_list(query_body, items)

        return items

    async def get_by_n_query(self, query_list: list[str]) -> Optional[list[ORJSONModel]]:
        result = []
        for query in query_list:
            tmp = await self.get_by_query(query)
            if tmp is not None:
                result = [*result, *tmp]

        return result

    async def get_by_n_property(self, property_list: list[str], property_value,
                                page_size: int = None, page_number: int = None, ):
        query_list = []
        for prop in property_list:
            q = QueryBuilder()
            if page_size is not None:
                q.set_pagination(page_number, page_size)
            parent_property = prop.split('.')[0]
            q.set_nested_match(parent_property, prop, property_value)
            query_list.append(q.get_query())

        return await self.get_by_n_query(query_list)

    async def uber_get(self, page_size: int = None,
                       page_number: int = None,
                       search_value: str = None,
                       search_fields: list[str] = None,
                       property_full_path: str = None,
                       property_list: list[str] = None,
                       sort_field: str = None
                       ):

        if property_list is not None:
            return await self.get_by_n_property(property_list, search_value, page_size, page_number)

        q = QueryBuilder()
        q.set_query_match_all()

        if (page_number is not None) and (page_size is not None):
            q.set_pagination(page_number, page_size)

        if (search_value is not None) and (search_fields is not None):
            q.set_fuzzy_query(search_value, search_fields)

        if (property_full_path is not None) and (search_value is not None):
            parent_property = property_full_path.split('.')[0]
            q.set_nested_match(parent_property, property_full_path, search_value)

        if sort_field is not None:
            sort_order, sort_field = self.parseOrderField(sort_field)
            q.set_order(sort_field, sort_order)

        query_body = q.get_query()
        result = await self.get_by_query(query_body)
        return result

    def parseOrderField(self, field: str):
        if field[0] == "-":
            return 'desc', field[1:]
        else:
            return 'asc', field
