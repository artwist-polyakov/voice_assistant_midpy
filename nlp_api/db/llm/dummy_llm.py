from elasticsearch_dsl.query import Query, MultiMatch
from db.llm.base_llm import BaseLLM
from db.models.requests.base_request import BaseRequest

index_name = str


class DummyLLM(BaseLLM):
    async def get_query(self, request: BaseRequest) -> (index_name, Query):
        if "вездны" in request.query and "войн" in request.query:
            return ('movies',
                    MultiMatch(query="star wars", fields=['title^5', 'description']))
        raise NotImplementedError
