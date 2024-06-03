import asyncio
import logging
import ast
import time
import aio_pika
from aio_pika.pool import Pool
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


async def process_message(queue_name, message: aio_pika.IncomingMessage):
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


async def consume_from_queue(channel_pool: Pool, queue_name: str):
    async with channel_pool.acquire() as channel:
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await process_message(queue_name, message)


async def main():
    async def get_connection() -> aio_pika.abc.AbstractRobustConnection:
        return await aio_pika.connect_robust(
            f"amqp://{rabbit_settings.user}:{rabbit_settings.password}@{rabbit_settings.host}:{rabbit_settings.amqp_port}/"
        )

    connection_pool: Pool = Pool(get_connection, max_size=2)

    async def get_channel() -> aio_pika.Channel:
        async with connection_pool.acquire() as connection:
            return await connection.channel()

    channel_pool: Pool = Pool(get_channel, max_size=10)

    async with connection_pool, channel_pool:
        tasks = [consume_from_queue(channel_pool, queue_name) for queue_name in queues]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
