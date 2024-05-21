import logging
from http import HTTPStatus
import json
from api.v1.models.requests.nlp_request import QuestionParam
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from elasticsearch import Elasticsearch
from  langchain.chains import LLMChain
from langchain_community.llms import YandexGPT


from core.settings import get_settings

router = APIRouter()
settings = get_settings()
es = Elasticsearch(
    hosts=["http://elasticsearch:9200"],
    verify_certs=False
)

llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0, api_key=settings.openai_api_key)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are an assistant that converts natural language queries into Elasticsearch queries.
            Translate request to English language.
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
            
            Answer with only query content, without any additional text, and markdown formatting.
            Convert the following natural language query to an Elasticsearch query:
            """,
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | llm


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

    response = chain.invoke(params.text).dict()
    logging.info(f"Response: \n{response}")
    elasticsearch_query = json.loads(response['content'])
    result = es.search(index='movies', body=elasticsearch_query)
    logging.info(f"Result: \n{result}")


    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={'message': f'Question received: params={params.dict()}'}
    )
