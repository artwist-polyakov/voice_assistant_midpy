import json
import logging
from http import HTTPStatus
from api.v1.models.requests.nlp_request import QuestionParam
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from langchain import LLMChain, PromptTemplate
from elasticsearch import Elasticsearch
from langchain_community.vectorstores import ElasticVectorSearch
from langchain_community.llms import YandexGPT

from core.settings import get_settings

settings = get_settings()

router = APIRouter()
es = Elasticsearch(
    hosts=["http://elasticsearch:9200"]
)

template = """
You are an assistant that converts natural language queries into Elasticsearch queries.

Please translate any lanquage to english if needed. Write only the Elasticsearch query.
Markdown is not needed. Additional information is not needed.

Elasticsearch has several indices with the following schemas:

            MOVIES_INDEX_SCHEMA:
            - id (keyword)
            - imdb_rating (float)
            - genres (nested, with fields: id (keyword), name (text, analyzer: ru_en), description (text, analyzer: ru_en))
            - title (text, analyzer: ru_en, fields: raw (keyword))
            - description (text, analyzer: ru_en)
            - directors_names (text, analyzer: ru_en)
            - actors_names (text, analyzer: ru_en)
            - writers_names (text, analyzer: ru_en)
            - actors (nested, with fields: id (keyword), name (text, analyzer: ru_en))
            - writers (nested, with fields: id (keyword), name (text, analyzer: ru_en))
            - directors (nested, with fields: id (keyword), name (text, analyzer: ru_en))

            GENRES_INDEX_SCHEMA:
            - id (keyword)
            - name (text, analyzer: ru_en, fields: raw (keyword))
            - description (text, analyzer: ru_en)

            PERSONS_INDEX_SCHEMA:
            - id (keyword)
            - full_name (text, analyzer: ru_en, fields: raw (keyword))

Convert the following natural language query to an Elasticsearch query (no need any additional information):
{query}


"""

prompt = PromptTemplate(template=template, input_variables=["query"])
llm = YandexGPT(api_key=settings.yc_api_key,
                model_uri="gpt://b1gsfbseql2uigg6q996/yandexgpt/latest",
                temperature=0.1)
llm_chain = LLMChain(llm=llm,prompt=prompt)


@router.get(
    path='/ask',
    summary="Ask a question",
    description="Ask a question to the cinema bot"
)
async def ask_question(
        external_user_id: str,
        external_session_id: str,
        params: QuestionParam = Depends()
) -> JSONResponse:
    logging.info(f"Question received: external_user_id={external_user_id}, "
                 f"external_session_id={external_session_id}, "
                 f"params={params.dict()}")
    query = params.text
    elasticsearch_query = llm_chain.invoke(query)['text'][3:-3].strip()
    print(elasticsearch_query)
    request = json.loads(elasticsearch_query)
    response = es.search(index="movies", body=request)
    print(response)
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={'message': f'Question received: params={params.dict()}'}
    )
