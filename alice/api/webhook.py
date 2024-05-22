import logging

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

    await handle_dialog(request.dict(), response)

    logging.info('Response: %r', response)
    # response['response']['text'] = "Привет от Саши! " + response['response']['text']
    return JSONResponse(content=response)


async def handle_dialog(req, res):
    user_id = req['session']['user_id']
    session_id = req['session']['session_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }

        # res['response']['text'] = 'Привет! Купи слона!'
        res['response']['text'] = 'Привет! Расскажи, какое кино тебя интересует?'
        res['response']['buttons'] = get_suggests(user_id)
        return

    text = req['request']['original_utterance'].lower()

    result, status = await get_response(
        settings.nlp_server + settings.nlp_post + '/' + settings.nlp_endpoint,
        params={'external_user_id': user_id, 'external_session_id': session_id, 'text': text}
    )

    # Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо',
    ]:
        # Пользователь согласился, прощаемся.
        res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        return

    # Если нет, то убеждаем его купить слона!
    res['response']['text'] = 'Все говорят "%s", а ты купи слона!' % (
        req['request']['original_utterance']
    )
    res['response']['buttons'] = get_suggests(user_id)

    if status != 200:
        res['response']['text'] = 'Ошибка сервера'
        return

    res['response']['text'] = result['result']


def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests
