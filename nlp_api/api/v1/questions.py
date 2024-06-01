import logging
from http import HTTPStatus

from api.v1.models.requests.nlp_request import QuestionParam
from api.v1.models.requests.nlp_request import FilmResponse
from api.v1.models.requests.nlp_request import ErrorResponse
from db.models.requests.search_request import SearchRequest
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from service.base_service import BaseService
from service.dummy_service import get_queue_service

router = APIRouter()


@router.get(
    path='/ask',
    summary="Ask a question",
    description="Ask a question to the cinema bot",
    responses={
        200: {"model": FilmResponse, "description": "Успешный запрос. Возвращает информацию о фильме"},
        400: {"model": ErrorResponse, "description": "Некорректный запрос. Возвращает сообщение об ошибке"},
        404: {"model": ErrorResponse, "description": "Ресурс не найден. Возвращает сообщение об отсутствии данных"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера. Запрос не удался"}
    }
)
async def ask_question(
        external_user_id: str,
        external_session_id: str,
        external_message_id: str,
        params: QuestionParam = Depends(),
        search_service: BaseService = Depends(get_queue_service)
) -> JSONResponse:
    logging.info(f"Question received: external_user_id={external_user_id}, "
                 f"external_session_id={external_session_id}, "
                 f"external_message_id={external_message_id}, "
                 f"params={params.model_dump()}")
    result = await search_service.proceed_request(SearchRequest(
        external_user_id=external_user_id,
        external_session_id=external_session_id,
        external_message_id=external_message_id,
        query=params.text
    ))
    logging.info(f"Result: {result}")
    if result:
        film_name = result['data'][0]['title']
        film_rating = result['data'][0]['imdb_rating']
        film_description = result['data'][0]['description']
        id = result['data'][0]['id']
        actors_names = result['data'][0]['actors_names']
        directors_names = result['data'][0]['directors_names']
        genres = [it['name'] for it in result['data'][0]['genres']]
        return JSONResponse(
            status_code=HTTPStatus.OK,
            content={
                'result': f'Кажется вас заинтересует фильм "{film_name}"'
                          f' с рейтингом {film_rating}',
                'name': film_name,
                'rating': film_rating,
                'description': film_description,
                'id': id,
                'actors_names': actors_names,
                'directors_names': directors_names,
                'genres': genres
            }
        )
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={'result': "Запрос не удался"}
    )
