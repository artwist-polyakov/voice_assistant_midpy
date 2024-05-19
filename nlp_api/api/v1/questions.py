import logging
from http import HTTPStatus
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from api.v1.models.requests.nlp_request import QuestionParam

router = APIRouter()


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
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={'message': f'Question received: params={params.dict()}'}
    )