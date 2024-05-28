import logging

from core.settings import get_settings
from db.llm.llm_processor import LLMProcessor
from langchain import PromptTemplate
from langchain_community.llms import YandexGPT


class YandexGPTLLM(LLMProcessor):
    _llm: YandexGPT | None = None
    _settings = get_settings()

    def __init__(self):
        template: str = """
        Определи с поиском чего связан следущий запрос: поиск фильмов, поиск жанров или поиск персон.
        Запрос: {query}
        Если ты сомневаешься — отвечай none.
        У тебя есть 4 варианта ответа: movies, genres, persons, none. Ответь, пожалуйста, одним словом.
        """  # noqa: E501
        super().__init__(
            prompt_template=template,
            max_tokens=20,
            temperature=0.1,
            top_p=0.1)

        self._llm = YandexGPT(
            api_key=self._settings.yc_api_key,
            model_uri=self._settings.ya_gpt_model,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            top_p=self._top_p
        )
        self._prompt_template = PromptTemplate(template=template, input_variables=["query"])
        self._llm_chain = self._prompt_template | self._llm

    def process_query(self, message: str) -> str | None:
        answer = self._llm_chain.invoke(message).lower()
        logging.info(f'answer is {answer}')
        if 'none' in answer:
            return None
        if 'movies' in answer:
            return 'movies'
        if 'genres' in answer:
            return 'genres'
        if 'persons' in answer:
            return 'persons'
        return None
