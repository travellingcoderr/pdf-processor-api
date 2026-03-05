import certifi
from pymongo import AsyncMongoClient

from app.config import MONGO_URI

# Use certifi's CA bundle for Atlas (mongodb+srv) TLS; avoids SSL handshake errors in Docker
mongo_client: AsyncMongoClient = AsyncMongoClient(
    MONGO_URI,
    tlsCAFile=certifi.where(),
)
