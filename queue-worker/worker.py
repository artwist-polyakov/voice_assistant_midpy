import ast
import logging
import time
import asyncio
from core.prompts import Prompts
from core.settings import get_rabbit_settings
from db.cache.redis_cache import RedisCache
from db.llm.yandex_gpt import YandexGPTLLM
from db.queues.rabbit_queue import RabbitQueue
from models.search_request import SearchRequest
import aio_pika

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

    async def async_handler(message: aio_pika.IncomingMessage):
        async with message.process():
            try:
                data = SearchRequest(**ast.literal_eval(message.body.decode()))
                logger.info("Processing | %s | %s", queue_key, data)
                start_time = time.time()
                result = llm.process_query(data.query)
                logger.info("(%f sec)\nResult | %s | %s", time.time() - start_time, queue_key, result)
                redis_cli.put_cache(message.headers['Task-Id'] + redis_keys[queue_key], result if result else "None")
            except Exception as e:
                logger.error(f"Error in callback: {e}")

    def sync_handler(message):
        asyncio.create_task(async_handler(message))

    return sync_handler


async def main():
    connection = await aio_pika.connect_robust(
        host=rabbit_settings.host,
        port=rabbit_settings.amqp_port,
        login=rabbit_settings.user,
        password=rabbit_settings.password
    )

    async with connection:
        channel = await connection.channel()

        tasks = []
        for queue_name in queues:
            queue_obj = await channel.declare_queue(queue_name, durable=True)
            handler = create_handler(queue_name)
            task = queue_obj.consume(handler)
            tasks.append(task)

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
