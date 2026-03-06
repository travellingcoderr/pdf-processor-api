import logging
from rq import Worker

from app.config import RQ_QUEUE_NAME
from app.queue.q import redis_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("RQ worker starting, queue=%s", RQ_QUEUE_NAME)
    worker = Worker([RQ_QUEUE_NAME], connection=redis_connection)
    worker.work()


if __name__ == "__main__":
    main()
