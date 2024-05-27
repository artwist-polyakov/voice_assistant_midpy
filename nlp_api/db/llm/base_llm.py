from abc import ABC, abstractmethod

from db.models.requests.search_request import SearchRequest
from elasticsearch_dsl.query import Query


class BaseLLM(ABC):
    @abstractmethod
    def get_query(self, request: SearchRequest) -> Query:
        pass
