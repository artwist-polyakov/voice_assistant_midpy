import logging

from db.llm_pipe.base_llm_pipe import BaseLLMPipe
from db.llm_pipe.redis_core import RedisCore


class RedisLLMPipe(BaseLLMPipe, RedisCore):

    @RedisCore.initialize
    async def get_keys_with_values(self, prefix: str) -> dict:
        logging.info(f"Getting keys with values by prefix: {prefix}")
        keys = await self._redis.keys(f"{prefix}*")
        logging.info(f"Keys: {keys}")
        if not keys:
            return {}
        values = await self._redis.mget(*keys)
        return dict(zip(keys, values))

    @RedisCore.initialize
    async def put_cache(self, key: str, value: str, expired=0) -> None:
        pass

    async def close(self):
        if self._redis is not None:
            await self._redis.close()
            self._redis = None

    async def get_cache(self, key: str) -> str:
        return await self._redis.get(key)
