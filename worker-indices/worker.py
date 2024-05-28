import ast
import logging
import time

from core.settings import get_rabbit_settings
from db.cache.redis_cache import RedisCache
from db.llm.yandex_gpt import YandexGPTLLM
from db.queues.rabbit_queue import RabbitQueue
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from models.search_request import SearchRequest

logger = logging.getLogger('creating-worker-logger')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

rabbitmq_indices = RabbitQueue(
    get_rabbit_settings().subject_queue
)

llm = YandexGPTLLM()
redis_cli = RedisCache()


def handler(
        ch: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes
):
    try:
        data = SearchRequest(**ast.literal_eval(body.decode()))
        logger.info(f"Processing | indice_parcer | {data}")
        start_time = time.time()
        result = llm.process_query(data.query)
        logger.info(f"({time.time()-start_time}sec)\nResult | indice_parcer | {result}")
        redis_cli.put_cache(properties.headers['Task-Id'] + '_index', result if result else "None")
    except Exception as e:
        logging.error(f"Error in callback: {e}")


try:
    rabbitmq_indices.pop(handler=handler)
except Exception as e:
    logger.error(f"Error in worker: {e}")
