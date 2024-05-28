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
Ты компьютер, который анализирует запросы на наличие уточнений по упорядочиванию результатов по рейтингу.
Определи, содержится ли в данном запросе уточнение по упорядочиванию результатов по рейтингу/популярнности.
Запрос: {query}
Если ты сомневаешься, отвечай: none.
Ответ должен быть однословним: asc, desc или none.
Примеры:
Запрос: "покажи фильмы с самым высоким рейтингом"
Ответ: desc
Запрос: "самые плохие работы тарантино"
Ответ: asc
Запрос: "какие фильмы сейчас готовятся к выходу"
Ответ: none
"""  # noqa: E501
        super().__init__(
            prompt_template=template,
            max_tokens=20,
            temperature=0.1,
            top_p=0.1)

        self._llm = YandexGPT(
            api_key=self._settings.yc_api_key,
            model_uri="gpt://b1gsfbseql2uigg6q996/yandexgpt/latest",
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
        return answer
