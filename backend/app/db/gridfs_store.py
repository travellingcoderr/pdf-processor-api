"""
Sync GridFS storage so both API and worker can read/write PDFs via MongoDB.
Used when API and worker run in different containers (e.g. Railway) with no shared disk.
"""
import certifi
from bson import ObjectId
from gridfs import GridFS
from pymongo import MongoClient

from app.config import MONGO_DB_NAME, MONGO_URI, MONGO_TLS_INSECURE

_sync_client: MongoClient | None = None
_fs: GridFS | None = None


def _get_sync_client() -> MongoClient:
    global _sync_client
    if _sync_client is None:
        _sync_client = MongoClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=MONGO_TLS_INSECURE,
        )
    return _sync_client


def _get_fs() -> GridFS:
    global _fs
    if _fs is None:
        db = _get_sync_client()[MONGO_DB_NAME]
        _fs = GridFS(db)
    return _fs


def put_file(data: bytes, filename: str) -> ObjectId:
    """Store file in GridFS; returns the GridFS file _id."""
    return _get_fs().put(data, filename=filename)


def get_file(gridfs_id: str) -> bytes:
    """Read file from GridFS by id (str or ObjectId)."""
    oid = ObjectId(gridfs_id)
    grid_out = _get_fs().get(oid)
    return grid_out.read()
