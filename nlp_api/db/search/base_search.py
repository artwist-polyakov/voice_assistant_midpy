from abc import ABC, abstractmethod

from db.llm.base_llm import BaseLLM
from db.models.requests.search_request import SearchRequest
from db.models.responses.base_response import BaseResponse


class BaseSearch(ABC):

    def __init__(self, llm: BaseLLM):
        self._llm = llm

    @abstractmethod
    async def handle_request(self, request: SearchRequest) -> BaseResponse | None:
        pass

    @abstractmethod
    async def close(self):
        pass
