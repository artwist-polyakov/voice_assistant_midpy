from typing import Callable, TypeVar

import pika
from db.queues.base_queue import BaseQueue

from core.settings import get_rabbit_settings

T = TypeVar('T')


class RabbitQueue(BaseQueue):
    def __init__(self, key: str):
        self.host = get_rabbit_settings().host
        self.port = get_rabbit_settings().amqp_port
        self.username = get_rabbit_settings().user
        self.password = get_rabbit_settings().password
        self.connection = None
        self.channel = None
        self._key = key

    def __enter__(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()

    def push(self, message: T, session=None):
        pass

    def pop(self,
            handler: Callable[
                [pika.channel.Channel,
                 pika.spec.Basic.Deliver,
                 pika.spec.BasicProperties,
                 bytes],
                None
            ]):
        with self:
            self.channel.basic_consume(
                queue=self._key,
                on_message_callback=handler,
                auto_ack=False
            )
            self.channel.start_consuming()

    def close(self):
        pass
