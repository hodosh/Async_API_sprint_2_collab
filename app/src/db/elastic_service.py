from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError

from models.models import ORJSONModel


class ElasticService:
    def __init__(self, elastic: AsyncElasticsearch, elastic_index: str, model: ORJSONModel):
        self.elastic = elastic
        self.elastic_index = elastic_index
        self.model = model

    # получение документа по ID
    async def get_by_id(self, item_id: str) -> Optional[ORJSONModel]:
        try:
            doc = await self.elastic.get(index=self.elastic_index, id=item_id)
        except NotFoundError:
            return None
        return self.model(**doc['_source'])

    # получение документов по запросу
    async def get_by_query(self, query_body: str) -> Optional[list[ORJSONModel]]:
        try:
            raw_result = await self.elastic.search(index=self.elastic_index, doc_type="_doc", body=query_body)
        except NotFoundError:
            return None
        else:
            return [self.model(**doc['_source']) for doc in raw_result['hits']['hits']]
