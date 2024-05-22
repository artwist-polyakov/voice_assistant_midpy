import logging
from functools import lru_cache

from db.llm.dummy_llm import DummyLLM
from db.models.requests.search_request import SearchRequest
from db.search.elastic_search import ElasticSearch
from service.base_service import BaseService


class DummyService(BaseService):
    async def proceed_request(self, request: SearchRequest) -> dict | None:
        result = await self._search.handle_request(request)
        return result.model_dump()['data'] if result else None


@lru_cache
def get_dummy_service() -> BaseService:
    search = ElasticSearch(DummyLLM())
    return DummyService(search)
