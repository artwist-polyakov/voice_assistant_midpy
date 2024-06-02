import ast
import json
import logging
import time

from core.settings import get_rabbit_settings
from db.cache.redis_cache import RedisCache
from db.llm.yandex_gpt import YandexGPTLLM
from db.queues.rabbit_queue import RabbitQueue
from models.search_request import SearchRequest
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

logger = logging.getLogger('actors-worker-logger')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

rabbitmq_indices = RabbitQueue(
    get_rabbit_settings().actor_queue
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
        logger.info('Processing | actor_parser | %s', json.dumps(data))
        start_time = time.time()
        result = llm.process_query(data.query)
        logger.info(
            '(%(seconds).3fsec)\nResult | actor_parser | %(result)s',
            {
                'seconds': time.time()-start_time,
                'result': result,
            }
        )
        redis_cli.put_cache(properties.headers['Task-Id'] + '_actor', result if result else "None")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logging.error('Error in callback: %s', str(e))


try:
    rabbitmq_indices.pop(handler=handler)
except Exception as e:
    logger.error('Error in worker: %s', str(e))
