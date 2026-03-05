from redis import Redis
from rq import Queue

from app.config import (
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
    REDIS_URL,
    RQ_QUEUE_NAME,
    REDIS_SOCKET_CONNECT_TIMEOUT,
    REDIS_SOCKET_TIMEOUT,
    REDIS_HEALTH_CHECK_INTERVAL,
)

if REDIS_URL:
    # Remote Redis (e.g. Upstash rediss://): use longer timeouts and fewer health checks
    redis_connection = Redis.from_url(
        REDIS_URL,
        socket_connect_timeout=REDIS_SOCKET_CONNECT_TIMEOUT,
        socket_timeout=REDIS_SOCKET_TIMEOUT,
        health_check_interval=REDIS_HEALTH_CHECK_INTERVAL,
    )
else:
    redis_connection = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD or None,
    )

q = Queue(name=RQ_QUEUE_NAME, connection=redis_connection)
