from redis import Redis
from rq import Queue

from app.config import REDIS_HOST, REDIS_PORT, RQ_QUEUE_NAME

redis_connection = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
)

q = Queue(name=RQ_QUEUE_NAME, connection=redis_connection)
