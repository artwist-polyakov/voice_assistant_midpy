import logging
import logging.config
import random
import time
import traceback
from functools import wraps

from configs.log_config import base_logging_config


def configure_logger(config_file: dict = base_logging_config):
    logging.config.dictConfig(config_file)


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Декоратор для повторного выполнения функции.

    в случае возникновения исключения
    использует экспоненциальную задержку + jitter
    но не более border_sleep_time
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    sleep_time = min(
                        border_sleep_time, start_sleep_time * factor * attempt
                    )
                    sleep_with_jitter = random.uniform(0, sleep_time)
                    error_traceback = traceback.format_exc()
                    logging.error(
                        'Error: %(error)s. Retrying in %(sleep_with_jitter).3f seconds...\n \
                            %(error_traceback)s',
                        {
                            'error': str(error),
                            'sleep_with_jitter': sleep_with_jitter,
                            'error_traceback': error_traceback
                        }
                    )
                    time.sleep(sleep_with_jitter)
                    attempt += 1

        return inner

    return func_wrapper
