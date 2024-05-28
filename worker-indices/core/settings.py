import logging
from functools import lru_cache

from core.logging_setup import setup_root_logger
from pydantic_settings import BaseSettings, SettingsConfigDict

log_levels = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR
}

setup_root_logger()


class Settings(BaseSettings):
    logging_level: str = "INFO"

    sentry_dsn: str = ...
    sentry_enable_tracing: bool = True

    redis_db: int = 8
    redis_host: str = ...
    redis_port: int = ...

    yc_api_key: str = ...
    ya_gpt_model: str = ...

    def get_logging_level(self) -> int:
        return log_levels.get(self.logging_level, logging.INFO)

    class Config:
        env_file = '.env'


class RabbitSettings(BaseSettings):
    """Настройки Rabbit."""

    model_config = SettingsConfigDict(env_prefix="rabbit_mq_")
    host: str
    port: int
    amqp_port: int
    user: str
    password: str
    exchange: str
    subject_queue: str


settings = Settings()


@lru_cache
def get_settings():
    return settings


@lru_cache
def get_rabbit_settings():
    return RabbitSettings()
