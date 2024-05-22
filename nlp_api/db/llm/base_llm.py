from abc import ABC, abstractmethod

from db.models.requests.base_request import BaseRequest
from elasticsearch_dsl.query import Query


class BaseLLM(ABC):
    @abstractmethod
    def get_query(self, request: BaseRequest) -> Query:
        pass
