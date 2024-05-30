import asyncio
import datetime
import logging
import re
import time

from db.llm.base_llm import BaseLLM
from db.llm_pipe.redis_llm_pipe import RedisLLMPipe
from db.models.requests.search_request import SearchRequest
from db.queue.rabbit_queue import RabbitQueue
from elasticsearch_dsl.query import MultiMatch, Query
from elasticsearch_dsl.search import Search, Q

index_name = str


class QueueLLM(BaseLLM):
    _queue = RabbitQueue()
    _llm_pipe = RedisLLMPipe()

    async def get_query(self, request: SearchRequest) -> (index_name, Query):
        self._queue.push(task=request)
        await asyncio.sleep(2)
        prefix = "-".join([
            request.external_user_id,
            request.external_session_id,
            request.external_message_id
        ])
        pipe_result = await self._llm_pipe.get_keys_with_values(prefix=prefix)

        logging.info(f"Got result from pipe: {QueueLLM._preprocess_pipe_result(pipe_result)}")
        # if "вездны" in request.query and "войн" in request.query:
        #     return ('movies',
        #             MultiMatch(query="star wars", fields=['title^5', 'description']))
        # raise NotImplementedError
        query = Query()
        return (QueueLLM.get_index(pipe_result),
                QueueLLM.configure_query(pipe_result, query))

    @staticmethod
    def get_index(preproc_data: dict) -> index_name | None:
        index = preproc_data.get('index', None)
        if index is None or index == 'movies':
            return 'movies'
        return index

    @staticmethod
    def configure_query(preproc_data: dict, search: Search) -> Search:
        for key, value in preproc_data.items():
            if value is None:
                continue
            if isinstance(value, list):
                value = ' '.join(value)
            match key:
                case 'title':
                    search = search.query(MultiMatch(query=value, fields=['title^5']))
                case 'description':
                    search = search.query(MultiMatch(query=value, fields=['description']))
                case 'actor':
                    search = search.query(MultiMatch(query=value, fields=['actors_names']))
                case 'director':
                    search = search.query(MultiMatch(query=value, fields=['directors_names']))
                case 'genre':
                    search = search.query(MultiMatch(query=value, fields=['genres']))
                # case 'date':
                # for date_condition in value:
                #     params = date_condition.split(':')
                #     if params[1] == 'now':
                #         query = query.Range(release_date={'lte': datetime.now().strftime('%Y-%m-%d')})
                #     elif params[0] == 'gt':
                #         query = query.Range(release_date={'gt': params[1]})
                #     elif params[0] == 'lt':
                #         query = query.Range(release_date={'lt': params[1]})
                case 'rating':
                    if 'asc' in value:
                        search = search.sort('imdb_rating')
                    if 'desc' in value:
                        search = search.sort('-imdb_rating')
                case _:
                    pass
        return search

    @staticmethod
    def _get_last_part_of_key(key: str) -> str:
        return key.split('_')[-1]

    @staticmethod
    def _is_none_value(value: str):
        return value.strip().lower() == "none"

    @staticmethod
    def _split_values(value: str):
        return value.split(',')

    @staticmethod
    def _clean_phrase(phrase):
        return re.sub(r'[^a-zA-Zа-яА-Я0-9 ]', '', phrase).lower()

    @staticmethod
    def _preprocess_pipe_result(pipe_result: dict):
        processed_result = {}
        for key, value in pipe_result.items():
            key_part = QueueLLM._get_last_part_of_key(key.decode('utf-8'))
            value_str = value.decode('utf-8')

            if QueueLLM._is_none_value(value_str):
                processed_result[key_part] = None
            else:
                phrases = QueueLLM._split_values(value_str)
                cleaned_phrases = [QueueLLM._clean_phrase(phrase) for phrase in phrases]
                processed_result[key_part] = cleaned_phrases

        return processed_result
