import logging
import aiohttp
from http import HTTPStatus

from api.v1.models.request_model import RequestBody
from core.settings import get_settings
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from utils.base_functions import get_response

router = APIRouter()
sessionStorage = {}
settings = get_settings()


@router.post("/")
async def main(request: RequestBody):
    logging.info('Request: %r', request.dict())

    response = {
        "version": request.version,
        "session": {
            "message_id": request.session.message_id,
            "session_id": request.session.session_id,
            "skill_id": request.session.skill_id,
            "user_id": request.session.user_id
        },
        "response": {
            "end_session": False
        }
    }

    session = aiohttp.ClientSession(cookies=None)
    await handle_dialog(request.dict(), response, session)

    logging.info('Response: %r', response)
    session.close()
    # response['response']['text'] = "Привет от Саши! " + response['response']['text']
    return JSONResponse(content=response)


async def handle_dialog(req, res, session):
    user_id = req['session']['user_id']
    session_id = req['session']['session_id']
    message_id = req['session']['message_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'suggests': [
                "Спасибо",
                "Подходит",
                "Написать в поддержку",
            ],
            'need_support': False
        }

        res['response']['text'] = 'Привет! Расскажи, какое кино тебя интересует?'
        res['response']['buttons'] = get_suggests(user_id, session)
        return

    text = req['request']['original_utterance'].lower()

    # По умолчанию эйндпоинт - поиск фильма
    endpoint = settings.nlp_endpoint

    # обрабатываем обратную связь от пользоватлея
    if sessionStorage[user_id].get('need_support'):
        # Если в предыдущий раз пользователь нажал на "поддержку"
        # то запрос отправляем на ручку с обратной связью
        endpoint = settings.support_endpoint
        sessionStorage[user_id]['need_support'] = False

    # Обрабатываем ответ пользователя.
    if text in [
        'спасибо',
        'подходит'
    ]:
        # Пользователь согласился, прощаемся.
        res['response']['text'] = 'Приятного просмотра!'
        return

    # Просим сформулировать вопрос, если хочет написать в поддержку
    if text in [
        'написать в поддержку',
        'поддержка',
        'запрос в поддержку'
    ]:
        # Запоминаем, чтобы при следующем запросе обработать его
        sessionStorage[user_id]['need_support'] = True
        res['response']['text'] = 'Напишите, пожалуйста, ваш запрос в поддержку.'
        return

    result, status = await get_response(
        session,
        'http://' +
        settings.nlp_server + ':' +
        str(settings.nlp_port) + '/' +
        endpoint,
        params={
            'external_user_id': user_id,
            'external_session_id': session_id,
            'external_message_id': message_id,
            'text': text}
    )

    res['response']['buttons'] = get_suggests(user_id, session)

    if status not in [HTTPStatus.OK, HTTPStatus.NO_CONTENT]:
        res['response']['text'] = 'Ошибка сервера'
        return

    if status == HTTPStatus.NO_CONTENT:
        res['response']['text'] = 'По вашему запросу ничего не найдено.'
        return

    res['response']['text'] = result['result']


def get_suggests(user_id, session):

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]

    return suggests
