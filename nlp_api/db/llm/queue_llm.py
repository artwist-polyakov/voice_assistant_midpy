import asyncio
import logging

from db.llm.base_llm import BaseLLM
from db.llm_pipe.redis_llm_pipe import RedisLLMPipe
from db.models.requests.search_request import SearchRequest
from db.queue.rabbit_queue import RabbitQueue
from elasticsearch_dsl.query import MultiMatch, Query

index_name = str


class QueueLLM(BaseLLM):
    _queue = RabbitQueue()
    _llm_pipe = RedisLLMPipe()

    async def get_query(self, request: SearchRequest) -> (index_name, Query):
        self._queue.push(task=request)
        await asyncio.sleep(3)
        prefix = "-".join([
            request.external_user_id,
            request.external_session_id,
            request.external_message_id
        ])
        pipe_result = await self._llm_pipe.get_keys_with_values(prefix=prefix)
        logging.info(f"Got result from pipe: {pipe_result}")
        if "вездны" in request.query and "войн" in request.query:
            return ('movies',
                    MultiMatch(query="star wars", fields=['title^5', 'description']))
        raise NotImplementedError
