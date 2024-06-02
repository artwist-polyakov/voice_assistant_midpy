from abc import ABC, abstractmethod


class LLMProcessor(ABC):

    def __init__(self, prompt_template: str, max_tokens: int, temperature: float, top_p: float):
        self._prompt_template = prompt_template
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._top_p = top_p

    @abstractmethod
    def process_query(self, message: str) -> str | None:
        pass
