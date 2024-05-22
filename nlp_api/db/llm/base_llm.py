from abc import ABC, abstractmethod
from elasticsearch_dsl.query import Query

from db.models.requests.base_request import BaseRequest


class BaseLLM(ABC):
    @abstractmethod
    def get_query(self, request: BaseRequest) -> Query:
        pass
