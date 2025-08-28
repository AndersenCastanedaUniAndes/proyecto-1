import redis.asyncio as redis
import json
import os
import logging

redis_client = None


def _get_redis_url():
    return os.getenv("REDIS_URL", "redis://localhost:6379")


async def init_redis():
    global redis_client
    url = _get_redis_url()
    logging.getLogger(__name__).info(f"Conectando a Redis en {url}")
    redis_client = redis.from_url(url, decode_responses=True)


async def publish_event(event_type, payload):
    if not redis_client:
        raise RuntimeError("Redis no inicializado; invoca init_redis() en startup")

    event = {"type": event_type, "payload": payload}
    logging.getLogger(__name__).debug(f"Publicando evento {event_type}: {payload}")
    await redis_client.publish("events", json.dumps(event))
