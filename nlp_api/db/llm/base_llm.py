from abc import ABC, abstractmethod

from elasticsearch_dsl.query import Query

from db.models.requests.search_request import SearchRequest


class BaseLLM(ABC):
    @abstractmethod
    def get_query(self, request: SearchRequest) -> Query:
        pass
