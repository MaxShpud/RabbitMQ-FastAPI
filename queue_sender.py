import asyncio
from rabbit_client import RabbitClient

SERVICE = 'TestService' # -- queue name
CLIENT = RabbitClient("amqp://guest:guest@127.0.0.1/%2F")


# ---------------------------------------------------------
#
async def sender():
    for idx in range(1, 11):
        routing_key = 'filestorage.getfile.query'
        if idx % 2 == 0:
            routing_key = 'filestorage.postfile.query'

        msg = {"title": f"message no {idx}"}

        await CLIENT.send_message(msg, routing_key)


# ---------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(sender())
