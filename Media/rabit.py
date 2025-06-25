### rabit.py
import os
import aio_pika
import json

import os
RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@localhost:5672/")
# RABBIT_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


async def get_channel():
    conn = await aio_pika.connect_robust(RABBIT_URL)
    return await conn.channel()


async def publish_event(routing_key: str, message: dict):
    channel = await get_channel()
    await channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps(message).encode()),
        routing_key=routing_key
    )