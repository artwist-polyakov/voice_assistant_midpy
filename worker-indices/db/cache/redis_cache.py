from db.cache.base_cache import BaseCache
from db.cache.redis_core import RedisCore


class RedisCache(BaseCache, RedisCore):

    @RedisCore.initialize
    def put_cache(self, key: str, value: str, expired=0) -> None:
        


    def close(self):
        pass

    def get_cache(self, key: str) -> str:
        pass