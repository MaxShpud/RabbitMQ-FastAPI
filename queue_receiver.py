import asyncio
import contextlib
from rabbit_client import RabbitClient

SERVICE = 'TestService'


# ---------------------------------------------------------
#
async def process_incoming_message(message: dict):
    print(f'Received: {message}')


# ---------------------------------------------------------
#
async def receiver():
    print('Started RabbitMQ message queue subscription...')
    client = RabbitClient("amqp://guest:guest@127.0.0.1/%2F", SERVICE, process_incoming_message)
    connection = await asyncio.create_task(client.consume())

    try:
        # Wait until terminate
        await asyncio.Future()

    finally:
        await connection.close()


# ---------------------------------------------------------

if __name__ == "__main__":

    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(receiver())