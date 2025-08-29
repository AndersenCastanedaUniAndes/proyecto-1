from fastapi.encoders import jsonable_encoder
import redis.asyncio as redis
import json, os, logging, uuid
from redis import Redis

redis_client: Redis = None


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

    event = {
        "id"      : str(uuid.uuid4()),
        "type"    : event_type,
        "payload" : payload
    }

    print(f"\nEvento publicado: {event}\n")

    encoded_event = jsonable_encoder(event)
    logging.getLogger(__name__).debug(f"Publicando evento {event_type}: {payload}")
    await redis_client.publish("events", json.dumps(encoded_event))
