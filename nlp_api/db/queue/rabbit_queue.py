from typing import Any, Callable

import pika

from core.settings import get_rabbit_settings
from db.models.requests.search_request import SearchRequest
from db.queue.base_queue import BaseQueue


class RabbitQueue(BaseQueue):
    def __init__(self):
        self.host = get_rabbit_settings().host
        self.port = get_rabbit_settings().amqp_port
        self.username = get_rabbit_settings().user
        self.password = get_rabbit_settings().password
        self.connection = None
        self.channel = None

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

    def push(self, task: SearchRequest, session=None):
        with self:
            self.channel.confirm_delivery()
            task_id = "-".join([
                task.external_user_id,
                task.external_session_id,
                task.external_message_id
            ])
            properties = pika.BasicProperties(
                delivery_mode=2,
                headers={"Task-Id": task_id}
            )
            self.channel.basic_publish(
                exchange=get_rabbit_settings().exchange,
                routing_key='',
                body=str(task.model_dump()),
                properties=properties
            )

    def pop(self, handler: Callable[[Any, Any, Any, bytes], None]):
        with self:
            method_frame, header_frame, body = self.channel.basic_get(
                queue=self._key,
                auto_ack=False,
                on_message_callback=handler
            )

    def close(self):
        pass
