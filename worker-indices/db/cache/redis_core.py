from abc import ABC
from functools import wraps

from core.settings import get_settings

from redis import Redis


class RedisCore(ABC):
    _settings = get_settings()
    _redis: Redis | None = None

    @staticmethod
    def initialize(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            if self._redis is None:
                self._redis = Redis(
                    host=self._settings.redis_host,
                    port=self._settings.redis_port,
                    db=self._settings.redis_db,
                )
            return func(self, *args, **kwargs)

        return inner
