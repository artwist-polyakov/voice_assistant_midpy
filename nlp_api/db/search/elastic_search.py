import logging
from functools import wraps

from core.settings import ElasticSettings
from db.models.requests.search_request import SearchRequest
from db.models.responses.base_response import BaseResponse
from db.models.responses.search_response import SearchResponse
from db.search.base_search import BaseSearch
from elasticsearch import AsyncElasticsearch, NotFoundError


class ElasticSearch(BaseSearch):
    _settings = ElasticSettings()
    _elastic: AsyncElasticsearch | None = None

    @staticmethod
    def initialize(func):
        @wraps(func)
        async def inner(self, *args, **kwargs):
            if self._elastic is None:
                elastic_dsl = self._settings.model_dump()
                self._elastic = AsyncElasticsearch(**elastic_dsl)
            return await func(self, *args, **kwargs)

        return inner

    @initialize
    async def handle_request(self, request: SearchRequest) -> BaseResponse | None:
        result = None
        try:
            index, search = await self._llm.get_query(request)
            logging.info(f"Got query: {search.to_dict()}")
            logging.info(f"Got index: {index}")
            result = await self._elastic.search(index=index, body=search.to_dict())
            data = []
            for element in result['hits']['hits']:
                data.append(element['_source'])
            result = {'data': data}
        except NotFoundError:
            return result
        return SearchResponse(data=result) if result else result

    async def close(self):
        if self._elastic is not None:
            await self._elastic.close()
