import logging
from http import HTTPStatus

from api.v1.models.requests.nlp_request import QuestionParam
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from db.models.requests.search_request import SearchRequest
from service.base_service import BaseService
from service.dummy_service import get_dummy_service

router = APIRouter()


@router.get(
    path='/ask',
    summary="Ask a question",
    description="Ask a question to the cinema bot"
)
async def ask_question(
        external_user_id: str,
        external_session_id: str,
        params: QuestionParam = Depends(),
        search_service: BaseService = Depends(get_dummy_service)
) -> JSONResponse:
    logging.info(f"Question received: external_user_id={external_user_id}, "
                 f"external_session_id={external_session_id}, "
                 f"params={params.model_dump()}")
    result = await search_service.proceed_request(SearchRequest(
        external_user_id=external_user_id,
        external_session_id=external_session_id,
        query=params.text
    ))
    logging.info(f"Result: {result}")
    if result:
        film_name = result['data'][0]['title']
        film_rating = result['data'][0]['imdb_rating']
        return JSONResponse(
            status_code=HTTPStatus.OK,
            content={
                'result': f'Кажется вас заинтересует фильм "{film_name}" с рейтингом {film_rating}'}
        )
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={'result': "Запрос не удался"}
    )
