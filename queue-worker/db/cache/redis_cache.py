from db.cache.base_cache import BaseCache
from db.cache.redis_core import RedisCore

TIME_TO_STORE = 60 * 60 * 30  # 30 минут


class RedisCache(BaseCache, RedisCore):

    @RedisCore.initialize
    def put_cache(self, key: str, value: str, expired=TIME_TO_STORE) -> None:
        self._redis.set(key, value, ex=expired)

    def close(self):
        if self._redis is not None:
            self._redis.close()
            self._redis = None

    @RedisCore.initialize
    def get_cache(self, key: str) -> str:
        return self._redis.get(key)
