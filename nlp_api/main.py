import sentry_sdk
import uvicorn

from api.v1 import questions
from core.logger import LOGGING
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from core.settings import get_settings
from middlewares.logging_middleware import LoggingMiddleware

settings = get_settings()

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    enable_tracing=settings.sentry_enable_tracing,
)

app = FastAPI(
    title=settings.api_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse
)

app.add_middleware(LoggingMiddleware)

# Подключаем роутер к серверу, указав префикс /v1/films
# Теги указываем для удобства навигации по документации
app.include_router(questions.router, prefix='/api/v1/nlp', tags=['NLP'])

if __name__ == '__main__':
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=5556,
        log_config=LOGGING,
        log_level=settings.get_logging_level(),
    )
