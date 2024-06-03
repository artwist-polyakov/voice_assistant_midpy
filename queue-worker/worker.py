import asyncio
import logging
import ast
import time
from aio_pika import connect_robust, IncomingMessage, Message
from core.prompts import Prompts
from core.settings import get_rabbit_settings
from db.cache.redis_cache import RedisCache
from db.llm.yandex_gpt import YandexGPTLLM
from models.search_request import SearchRequest

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

redis_cli = RedisCache()
prompts_storage = Prompts()


async def process_message(queue_name, message: IncomingMessage):
    try:
        async with message.process():
            data = SearchRequest(**ast.literal_eval(message.body.decode()))
            logger.info(f"Processing | {queue_name} | {data}")
            start_time = time.time()
            llm = YandexGPTLLM(prompts_storage.get_prompt(queue_name))
            result = await llm.process_query(data.query)
            logger.info(f"Processing time | {queue_name} | {time.time() - start_time}")
            await redis_cli.put_cache(
                message.headers['Task-Id'] + redis_keys[queue_name],
                result if result else "None"
            )
            logger.info(f"Result | {queue_name} | {result}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")


async def consume_from_queue(connection, queue_name):
    channel = await connection.channel()
    queue = await channel.declare_queue(queue_name, durable=True)

    async for message in queue:
        await process_message(queue_name, message)


async def main():
    connection = await connect_robust(
        f"amqp://{rabbit_settings.user}:{rabbit_settings.password}@{rabbit_settings.host}:{rabbit_settings.amqp_port}/"
    )

    async with connection:
        tasks = [consume_from_queue(connection, queue_name) for queue_name in queues]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
