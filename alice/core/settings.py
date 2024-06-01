import logging
from functools import lru_cache

from core.logging_setup import setup_root_logger
from pydantic_settings import BaseSettings

log_levels = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR
}

setup_root_logger()


class Settings(BaseSettings):
    api_name: str = "Alice Webhook"
    logging_level: str = "INFO"

    sentry_dsn: str = ...
    sentry_enable_tracing: bool = True

    nlp_server: str = 'nlp-api'
    nlp_port: int = 5556
    nlp_endpoint: str = 'api/v1/nlp/ask'
    support_endpoint: str = 'api/v1/nlp/support'

    def get_logging_level(self) -> int:
        return log_levels.get(self.logging_level, logging.INFO)

    class Config:
        env_file = '.env'


settings = Settings()


@lru_cache
def get_settings():
    return settings
