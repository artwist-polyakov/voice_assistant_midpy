from db.llm.base_llm import BaseLLM
from db.models.requests.search_request import SearchRequest
from elasticsearch_dsl.query import MultiMatch, Query

index_name = str


class DummyLLM(BaseLLM):
    async def get_query(self, request: SearchRequest) -> (index_name, Query):
        if "вездны" in request.query and "войн" in request.query:
            return ('movies',
                    MultiMatch(query="star wars", fields=['title^5', 'description']))
        raise NotImplementedError
