from abc import ABC, abstractmethod
from typing import Any, Callable

from db.models.requests.search_request import SearchRequest


class BaseQueue(ABC):

    @abstractmethod
    def push(self, task: SearchRequest):
        pass

    @abstractmethod
    def pop(self, handler: Callable[[Any, Any, Any, bytes], None]):
        pass

    @abstractmethod
    def close(self):
        pass
