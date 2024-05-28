from db.cache.base_cache import BaseCache
from db.cache.redis_core import RedisCore


class RedisCache(BaseCache, RedisCore):

    @RedisCore.initialize
    async def put_cache(self, key: str, value: str, expired=0) -> None:
        pass

    async def close(self):
        pass

    async def get_cache(self, key: str) -> str:
        pass
