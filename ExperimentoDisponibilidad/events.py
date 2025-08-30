import json, os, logging, uuid
from fastapi.encoders import jsonable_encoder
import redis.asyncio as redis
from redis.exceptions import ResponseError
from redis import Redis

redis_client: Redis = None
EVENT_GROUP   = os.getenv("EVENT_GROUP", "projector")
STREAM_KEY    = os.getenv("EVENT_STREAM", "events-stream")
STREAM_MAXLEN = int(os.getenv("STREAM_MAXLEN", "100000"))

def _get_redis_url():
    return os.getenv("REDIS_URL", "redis://localhost:6379")


async def init_redis():
    """Conecta y asegura el stream + grupo (id=$ para leer solo nuevos)."""
    global redis_client
    url = _get_redis_url()
    logging.getLogger(__name__).info(
        f"Conectando a Redis en {url} | stream={STREAM_KEY} group={EVENT_GROUP}"
    )
    redis_client = redis.from_url(url, decode_responses=True)

    try:
        # Crea stream (si no existe) y grupo; si ya existe, ignora BUSYGROUP
        await redis_client.xgroup_create(name=STREAM_KEY, groupname=EVENT_GROUP, id="$", mkstream=True)
    except ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise


async def publish_event(event_type: str, payload: dict, event_id: str | None = None):
    """Publica evento duradero (Stream) con un event_id para idempotencia del proyector."""
    if not redis_client:
        raise RuntimeError("Redis no inicializado; llama init_redis() en startup")

    encoded_payload = jsonable_encoder(payload) # encoding payload por problema de json.dumps
    event = {
        "id"     : event_id or str(uuid.uuid4()),  # id lógico para idempotencia
        "type"   : event_type,
        "payload": json.dumps(encoded_payload)
    }

    await redis_client.xadd(STREAM_KEY, event, maxlen=STREAM_MAXLEN, approximate=True)
