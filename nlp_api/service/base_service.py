from abc import ABC, abstractmethod

from db.cache.base_cache import BaseCache
from db.models.requests.base_request import BaseRequest
from db.search.base_search import BaseSearch


class BaseService(ABC):

    def __init__(self, search: BaseSearch, cache: BaseCache | None = None):
        if cache is not None:
            self._cache = cache
        self._search = search

    @abstractmethod
    async def proceed_request(self, request: BaseRequest) -> str:
        pass
