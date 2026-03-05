from app.config import MONGO_DB_NAME

from .client import mongo_client

database = mongo_client[MONGO_DB_NAME]
