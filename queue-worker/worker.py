import ast
import asyncio
import logging
import time

from core.prompts import Prompts
from core.settings import get_rabbit_settings
from db.cache.redis_cache import RedisCache
from db.llm.yandex_gpt import YandexGPTLLM
from db.queues.rabbit_queue import RabbitQueue
from models.search_request import SearchRequest
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

logger = logging.getLogger('universal-worker-logger')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

rabbit_settings = get_rabbit_settings()

queues = [
    rabbit_settings.subject_queue,
    rabbit_settings.actor_queue,
    rabbit_settings.director_queue,
    rabbit_settings.date_filter_queue,
    rabbit_settings.description_text_queue,
    rabbit_settings.genre_filter_queue,
    rabbit_settings.rating_order_queue,
    rabbit_settings.title_text_queue
]

redis_keys = {
    rabbit_settings.subject_queue: '_index',
    rabbit_settings.actor_queue: '_actor',
    rabbit_settings.director_queue: '_director',
    rabbit_settings.date_filter_queue: '_date',
    rabbit_settings.description_text_queue: '_description',
    rabbit_settings.genre_filter_queue: '_genre',
    rabbit_settings.rating_order_queue: '_rating',
    rabbit_settings.title_text_queue: '_title'
}

rabbits = {}

for queue in queues:
    rabbits[queue] = RabbitQueue(queue)

# llm = YandexGPTLLM()
redis_cli = RedisCache()
prompts_storage = Prompts()


def create_handler(queue_key):
    llm = YandexGPTLLM(prompts_storage.get_prompt(queue_key))

    def internal_handler(
            ch: Channel,
            method: Basic.Deliver,
            properties: BasicProperties,
            body: bytes
    ):
        try:
            data = SearchRequest(**ast.literal_eval(body.decode()))
            logger.info(f"Processing | {queue_key} | {data}")
            start_time = time.time()
            result = llm.process_query(data.query)
            logger.info(f"({time.time() - start_time}sec)\nResult | {queue_key} | {result}")
            redis_cli.put_cache(
                properties.headers['Task-Id'] + redis_keys[queue_key],
                result if result else "None"
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"Error in callback: {e}")

    return internal_handler


async def main():
    tasks = []
    for queue_name in queues:
        task = asyncio.create_task(
            asyncio.to_thread(
                rabbits[queue_name].pop,
                handler=create_handler(queue_name)
            )
        )
        tasks.append(task)
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
