import logging
from functools import wraps

from core.settings import ElasticSettings
from db.models.requests.search_request import SearchRequest
from db.models.responses.base_response import BaseResponse
from db.models.responses.search_response import SearchResponse
from db.search.base_search import BaseSearch
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search


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
            index, query_list, sorting = await self._llm.get_query(request)
            logging.info(f"Got query: {query_list}")
            search = Search(using=self._elastic, index=index).query('bool', must=query_list).sort(sorting)
            result = await self._elastic.search(index=index, body=search.to_dict())
            data = []
            for element in result['hits']['hits']:
                data.append(element['_source'])
            result = {'data': data}
        except NotImplementedError:
            pass
        return SearchResponse(data=result) if result else result

    async def close(self):
        if self._elastic is not None:
            await self._elastic.close()
