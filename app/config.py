import os


MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:admin@mongo:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "mydb")
# Use REDIS_URL (e.g. Upstash: rediss://default:password@host:port) or REDIS_HOST + REDIS_PORT
REDIS_URL = os.getenv("REDIS_URL", "")
REDIS_HOST = os.getenv("REDIS_HOST", "valkey")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
RQ_QUEUE_NAME = os.getenv("RQ_QUEUE_NAME", "default")
UPLOAD_ROOT = os.getenv("UPLOAD_ROOT", "/mnt/uploads")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
