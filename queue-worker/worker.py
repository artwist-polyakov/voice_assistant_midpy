import logging
import asyncio
import ast
import time
from aio_pika import connect_robust
from aio_pika.abc import AbstractIncomingMessage
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


async def create_handler(queue_key):
    llm = YandexGPTLLM(prompts_storage.get_prompt(queue_key))

    async def internal_handler(message: AbstractIncomingMessage):
        async with message.process():
            try:
                data = SearchRequest(**ast.literal_eval(message.body.decode()))
                logger.info(f"Processing | {queue_key} | {data}")
                start_time = time.time()
                result = await llm.process_query(data.query)  # Асинхронный вызов
                logger.info(f"({time.time() - start_time}sec)\nResult | {queue_key} | {result}")

                await redis_cli.put_cache(
                    message.headers['Task-Id'] + redis_keys[queue_key],
                    result if result else "None"
                )
            except asyncio.CancelledError:
                logger.error("Task was cancelled")
                raise
            except Exception as e:
                logger.error(f"Error in callback: {e}")

    return internal_handler


async def rabbitmq_task():
    while True:
        try:
            connection = await connect_robust(
                "amqp://{user}:{password}@{host}:{port}/".format(
                    user=rabbit_settings.user,
                    password=rabbit_settings.password,
                    host=rabbit_settings.host,
                    port=rabbit_settings.amqp_port
                )
            )
            async with connection:
                tasks = []
                for queue_name in queues:
                    channel = await connection.channel()  # Creating channel
                    await channel.set_qos(prefetch_count=1)
                    queue = await channel.declare_queue(queue_name, durable=True)

                    handler = await create_handler(queue_name)
                    task = asyncio.create_task(queue.consume(handler))
                    tasks.append(task)

                logging.info("Started with tasks %d", len(tasks))
                await asyncio.gather(*tasks)
        except Exception as e:
            logging.error(f"rabbitmq_task exception: {e} {type(e)}")
        logging.error("rabbitMQ should never be here... sleep a little")
        await asyncio.sleep(2)


if __name__ == "__main__":
    logging.info('start asyncio loop')
    loop = asyncio.get_event_loop()
    loop.create_task(rabbitmq_task())

    try:
        loop.run_forever()
    except Exception as e:
        logging.error(f"loop.run_forever exception: {e}")
    except KeyboardInterrupt:
        logging.info("loop.run_forever: KeyboardInterrupt")
    finally:
        logging.info("stop forever loop")
        tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]
        for task in tasks:
            task.cancel()
        future = asyncio.gather(*tasks, return_exceptions=True)
        loop.run_until_complete(future)
        loop.close()
