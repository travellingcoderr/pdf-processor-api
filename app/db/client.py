from pymongo import AsyncMongoClient

from app.config import MONGO_URI

mongo_client: AsyncMongoClient = AsyncMongoClient(MONGO_URI)
