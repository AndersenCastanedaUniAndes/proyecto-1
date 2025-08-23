import redis.asyncio as redis
import json

redis_client = None

async def init_redis():
    global redis_client
    redis_client = redis.from_url("redis://localhost", decode_responses=True)

async def publish_event(event_type, payload):
    event = {"type": event_type, "payload": payload}
    await redis_client.publish("events", json.dumps(event))
