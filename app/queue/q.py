from redis import Redis
from rq import Queue

from app.config import (
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
    REDIS_URL,
    RQ_QUEUE_NAME,
)

if REDIS_URL:
    redis_connection = Redis.from_url(REDIS_URL)
else:
    redis_connection = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD or None,
    )

q = Queue(name=RQ_QUEUE_NAME, connection=redis_connection)
