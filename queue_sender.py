import asyncio
from rabbit_client import RabbitClient


SERVICE = 'TestService'
CLIENT = RabbitClient("amqp://guest:guest@127.0.0.1/%2F")


# ---------------------------------------------------------
#
async def sender():

    for idx in range(1, 11):
        msg = {"title": f"message no {idx}"}
        await CLIENT.send_message(msg, SERVICE)
        print(f'Sent message: {msg}')


# ---------------------------------------------------------

if __name__ == "__main__":

    asyncio.run(sender())