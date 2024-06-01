import logging
from http import HTTPStatus

from api.v1.models.requests.nlp_request import QuestionParam
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get(
    path='/support',
    summary="Send a request to support",
    description="Send a support request in case of an error"
)
async def support(
        external_user_id: str,
        external_session_id: str,
        external_message_id: str,
        params: QuestionParam = Depends(),
) -> JSONResponse:
    logging.info(f"Question received: external_user_id={external_user_id}, "
                 f"external_session_id={external_session_id}, "
                 f"external_message_id={external_message_id}, "
                 f"params={params.model_dump()}")
    logging.info(f"User feedback about error : {params.text}")
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={'result': "Спасибо за обратную связь!"}
    )


@router.get(
    path='/agree',
    summary="Agree with the response",
    description="Agree with the response of the question"
)
async def agree(
        external_user_id: str,
        external_session_id: str,
        external_message_id: str,
        params: QuestionParam = Depends(),
) -> JSONResponse:
    logging.info(f"Question received: external_user_id={external_user_id}, "
                 f"external_session_id={external_session_id}, "
                 f"external_message_id={external_message_id}, "
                 f"params={params.model_dump()}")
    logging.info("User agreed with the response")
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={'result': "Приятного просмотра!"}
    )
