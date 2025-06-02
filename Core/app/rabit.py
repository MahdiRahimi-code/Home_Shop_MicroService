import os#, asyncio
import aio_pika
import json

RABBIT_URL = os.getenv("RABBITMQ_URL")

_connection: aio_pika.RobustConnection | None = None
_channel: aio_pika.RobustChannel | None = None

async def get_channel() -> aio_pika.RobustChannel:
    global _connection, _channel
    if not _connection:
        _connection = await aio_pika.connect_robust(RABBIT_URL)
    if not _channel:
        _channel = await _connection.channel()
    return _channel

async def publish_event(routing_key: str, message: dict):
    ch = await get_channel()
    await ch.default_exchange.publish(
        aio_pika.Message(body=json.dumps(message).encode()),
        routing_key=routing_key
    )
