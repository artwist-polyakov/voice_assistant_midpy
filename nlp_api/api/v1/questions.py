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
Convert the following natural language query to an Elasticsearch query:

Query: {query}

Please translate any lanquage to english if needed. Write please only the Elasticsearch query.

There are 3 indices: movies, genres and persons. Persons could be directors or actors.
"""

prompt = PromptTemplate(template=template, input_variables=["query"])
llm = YandexGPT(api_key=settings.yc_api_key,
                model_uri="gpt://b1gsfbseql2uigg6q996/yandexgpt/latest")
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
    elasticsearch_query = llm_chain.invoke(query)
    print("Elasticsearch query:", elasticsearch_query)
    # response = es.search(index="movies", body=elasticsearch_query)
    # print(response)
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={'message': f'Question received: params={params.dict()}'}
    )
