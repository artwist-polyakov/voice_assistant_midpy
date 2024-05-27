import logging

from db.llm.base_llm import BaseLLM
from db.models.requests.base_request import BaseRequest
from elasticsearch_dsl.query import MultiMatch, Query

from db.models.requests.search_request import SearchRequest
from db.queue.rabbit_queue import RabbitQueue

index_name = str


class QueueLLM(BaseLLM):
    _queue = RabbitQueue()

    async def get_query(self, request: SearchRequest) -> (index_name, Query):
        self._queue.push(task=request)
        if "вездны" in request.query and "войн" in request.query:
            return ('movies',
                    MultiMatch(query="star wars", fields=['title^5', 'description']))
        raise NotImplementedError
