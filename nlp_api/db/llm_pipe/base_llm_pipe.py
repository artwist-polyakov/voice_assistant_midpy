from abc import ABC, abstractmethod


class BaseLLMPipe(ABC):
    @abstractmethod
    async def get_cache(self, key: str) -> str:
        pass

    @abstractmethod
    async def put_cache(self, key: str, value: str, expired=0) -> None:
        pass

    @abstractmethod
    async def get_keys_with_values(self, prefix: str) -> dict:
        pass

    @abstractmethod
    async def close(self):
        pass
