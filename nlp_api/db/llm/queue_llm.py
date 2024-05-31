import asyncio
import logging
import re

from db.llm.base_llm import BaseLLM
from db.llm_pipe.redis_llm_pipe import RedisLLMPipe
from db.models.requests.search_request import SearchRequest
from db.queue.rabbit_queue import RabbitQueue
from elasticsearch_dsl import Q, Search

index_name = str


class QueueLLM(BaseLLM):
    _queue = RabbitQueue()
    _llm_pipe = RedisLLMPipe()

    async def get_query(self, request: SearchRequest) -> (index_name, Search):
        self._queue.push(task=request)
        await asyncio.sleep(2)
        prefix = "-".join([
            request.external_user_id,
            request.external_session_id,
            request.external_message_id
        ])
        pipe_result = await self._llm_pipe.get_keys_with_values(prefix=prefix)
        prepr = QueueLLM._preprocess_pipe_result(pipe_result)
        logging.info(f"Got result from pipe: {prepr}")

        index = QueueLLM.get_index(prepr)
        search = Search(index=index)
        search = QueueLLM.configure_query(prepr, search)
        return index, search

    @staticmethod
    def get_index(preproc_data: dict) -> index_name:
        index = preproc_data.get('index', ['movies'])
        return index[0] if isinstance(index, list) else index

    @staticmethod
    def configure_query(preproc_data: dict, search: Search) -> Search:
        query_parts = []
        for key, value in preproc_data.items():
            if value is None:
                continue
            if isinstance(value, list):
                value = ' '.join(value)
            match key:
                case 'title':
                    query_parts.append(
                        Q('multi_match', query=value, fields=['title^5'], type='phrase')
                    )
                case 'description':
                    query_parts.append(
                        Q('multi_match', query=value, fields=['description'], type='phrase')
                    )
                case 'actor':
                    query_parts.append(
                        Q('multi_match', query=value, fields=['actors_names'], type='phrase')
                    )
                case 'director':
                    query_parts.append(
                        Q(
                            'multi_match',
                            query=value,
                            fields=['directors_names'],
                            type='phrase'
                        )
                    )
                case 'genre':
                    for genre in value.split():
                        if genre != 'none':
                            query_parts.append(
                                Q(
                                    'nested',
                                    path='genres',
                                    query=Q('match', genres__name=genre)
                                )
                            )
                case 'rating':
                    if 'asc' in value:
                        search = search.sort('imdb_rating')
                    elif 'desc' in value:
                        search = search.sort('-imdb_rating')
                # case 'date':
                #     date_conditions = value.split(':')
                #     if date_conditions[1] == 'now':
                #         query_parts.append(
                #         Q('range', release_date={'lte': datetime.now().strftime('%Y-%m-%d')})
                #         )
                #     elif date_conditions[0] == 'gt':
                #         query_parts.append(Q('range', release_date={'gt': date_conditions[1]}))
                #     elif date_conditions[0] == 'lt':
                #         query_parts.append(Q('range', release_date={'lt': date_conditions[1]}))
                case _:
                    pass

        if query_parts:
            search = search.query(
                'bool',
                should=query_parts,
                minimum_should_match=max(1, int(len(query_parts) * 0.75)))
        return search

    @staticmethod
    def _get_last_part_of_key(key: str) -> str:
        return key.split('_')[-1]

    @staticmethod
    def _is_none_value(value: str) -> bool:
        return value.strip().lower() == "none"

    @staticmethod
    def _split_values(value: str) -> list:
        return value.split(',')

    @staticmethod
    def _clean_phrase(phrase: str) -> str:
        return re.sub(r'[^a-zA-Zа-яА-Я0-9 ]', '', phrase).lower()

    @staticmethod
    def _preprocess_pipe_result(pipe_result: dict) -> dict:
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
