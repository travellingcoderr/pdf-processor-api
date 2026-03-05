from rq import Worker

from app.config import RQ_QUEUE_NAME
from app.queue.q import redis_connection


def main() -> None:
    # RQ worker blocks forever, polling Redis/Valkey for new jobs on the named queue.
    worker = Worker([RQ_QUEUE_NAME], connection=redis_connection)
    worker.work()


if __name__ == "__main__":
    main()
