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
    api_name: str = "NLP API"
    logging_level: str = "INFO"

    sentry_dsn: str = ...
    sentry_enable_tracing: bool = True

    elastic_host: str = ...
    elastic_port: int = 9200

    redis_host: str = ...
    redis_port: int = ...
    redis_db: int = 0
    redis_llm_pipeline: int = 8

    def get_logging_level(self) -> int:
        return log_levels.get(self.logging_level, logging.INFO)

    class Config:
        env_file = '.env'


settings = Settings()


class ElasticDsn(BaseSettings):
    scheme: str = 'http'
    host: str = settings.elastic_host
    port: int = settings.elastic_port


class ElasticSettings(BaseSettings):
    hosts: list[ElasticDsn] = [ElasticDsn()]
    timeout: int = 60
    max_retries: int = 10
    retry_on_timeout: bool = True


class RabbitSettings(BaseSettings):
    """Настройки Rabbit."""

    model_config = SettingsConfigDict(env_prefix="rabbit_mq_")
    host: str
    port: int
    amqp_port: int
    user: str
    password: str
    exchange: str


@lru_cache
def get_settings():
    return settings


@lru_cache
def get_rabbit_settings():
    return RabbitSettings()
