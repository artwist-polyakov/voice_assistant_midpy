from functools import lru_cache
import uvicorn
import sentry_sdk
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse, ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from api import webhook
from api.v1.models.request_model import RequestBody
from core.settings import get_settings
from middlewares.logging_middleware import LoggingMiddleware

settings = get_settings()
# Хранилище данных о сессиях.



sentry_sdk.init(
    dsn=settings.sentry_dsn,
    enable_tracing=settings.sentry_enable_tracing,
)

app = FastAPI(
    title=settings.api_name,
    default_response_class=ORJSONResponse
)

app.add_middleware(LoggingMiddleware)

app.include_router(webhook.router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5555)
