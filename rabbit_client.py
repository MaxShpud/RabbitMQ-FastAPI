import asyncio
from typing import Callable, Optional
import ujson as json
from aio_pika import connect, connect_robust, Message, DeliveryMode
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection


# -----------------------------------------------------------------------------
#
class RabbitClient:
    """ This class handles the communication with the RabbitMQ server.

    Note: the queue mechanism is implemented to take advantage of good
    horizontal message scaling when needed.

    Both Publisher and Consumer async handling is implemented.
    """
    rabbit_url: str = None

    # ---------------------------------------------------------
    #
    def __init__(self, rabbit_url: str, service: Optional[str] = None,
                 incoming_message_handler: Optional[Callable] = None):
        """ The class initializer.

        :param rabbit_url: RabbitMQ's connection string.
        :param service: Name of receiving service (when using consume).
        :param incoming_message_handler: Incoming message callback method.
        """

        # Unique parameters.
        self.rabbit_url = rabbit_url
        self.service_name = service
        self.message_handler = incoming_message_handler

    # ---------------------------------------------------------
    #
    @staticmethod
    async def _process_incoming_message(message: AbstractIncomingMessage):
        """ Processing incoming message from RabbitMQ.

        :param message: Received message.
        """

        # if message.body:
        #     print(message.routing_key.title())
        #     await self.message_handler(json.loads(message.body))
        #
        # await message.ack()

        async with message.process():
            if message.routing_key == 'file-storage.get-file.query':
                print("GET ", message.body)
            if message.routing_key == 'file-storage.post-file.command':
                print("POST ", message.body)

    # ---------------------------------------------------------
    #
    async def consume(self) -> AbstractRobustConnection:
        """ Setup message listener with the current running asyncio loop. """
        loop = asyncio.get_running_loop()

        # Perform receive connection.
        connection = await connect_robust(loop=loop, url=self.rabbit_url)

        # Creating receive channel and setting quality of service.
        channel = await connection.channel()

        # Creating exchange
        await channel.declare_exchange(name='ic-exchange', type='topic')

        # Getting exchange
        await channel.get_exchange(name='ic-exchange')

        # To make sure the load is evenly distributed between the workers.
        await channel.set_qos(1)

        # Creating a receive queue.
        queue = await channel.declare_queue(name=self.service_name, durable=True)

        # Binding queues
        await queue.bind(exchange='ic-exchange', routing_key='file-storage.get-file.query')
        await queue.bind(exchange='ic-exchange', routing_key='file-storage.post-file.command')

        # Start consumption of existing and future messages.
        await queue.consume(self._process_incoming_message, no_ack=False)

        return connection

    # ---------------------------------------------------------
    #
    @classmethod
    async def send_message(cls, message: dict, routing_key: str):
        """ Send message to RabbitMQ Publisher queue.

        If the topic is defined, topic message routing is used, otherwise
        queue message routing is used.

        :param message: Message to be sent.
        :param queue: Message queue to use for message sending.
        :raise AssertionError: Parameters 'topic' and 'queue' are mutually exclusive.
        """
        connection = await connect(url=cls.rabbit_url)
        channel = await connection.channel()

        exchange = await channel.get_exchange(name='ic-exchange')

        message_body = Message(
            content_type='application/json',
            body=json.dumps(message, ensure_ascii=False).encode(),
            delivery_mode=DeliveryMode.PERSISTENT, reply_to=f"HELLO {message}")

        await exchange.publish(message=message_body, routing_key=routing_key)

        #await channel.default_exchange.publish(routing_key=queue, message=message_body)