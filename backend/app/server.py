import asyncio

from fastapi import FastAPI, UploadFile, Path
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .db.collections.files import files_collection, FileSchema
from .db.gridfs_store import put_file
from .queue.q import q
from .queue.workers import process_file_job
from bson import ObjectId
from bson.errors import InvalidId

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def hello():
    return {"status": "healthy"}


@app.get("/{id}")
async def get_file_by_id(id: str = Path(..., description="ID of the file")):
    try:
        oid = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=404, detail="File not found")
    db_file = await files_collection.find_one({"_id": oid})
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    return {
        "_id": str(db_file["_id"]),
        "name": db_file["name"],
        "status": db_file["status"],
        "result": db_file["result"] if "result" in db_file else None,
    }


@app.post("/upload")
async def upload_file(
    file: UploadFile
):
    db_file = await files_collection.insert_one(
        document=FileSchema(name=file.filename, status="saving")
    )
    file_id = str(db_file.inserted_id)
    file_bytes = await file.read()

    # Store PDF in GridFS so worker (different container) can read it
    loop = asyncio.get_event_loop()
    gridfs_id = await loop.run_in_executor(
        None, lambda: put_file(file_bytes, file.filename or "document.pdf")
    )

    q.enqueue(process_file_job, file_id, str(gridfs_id))

    await files_collection.update_one(
        {"_id": db_file.inserted_id},
        {"$set": {"status": "queued"}},
    )

    return {"file_id": file_id}
