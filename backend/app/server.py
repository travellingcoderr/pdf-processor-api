import asyncio
import os

from fastapi import FastAPI, UploadFile, Path
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .db.collections.files import files_collection, FileSchema
from .db.gridfs_store import put_file
from .queue.q import q
from .queue.workers import process_file_job
from .utils.docx_to_pdf import docx_to_pdf
from bson import ObjectId
from bson.errors import InvalidId

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

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


def _pdf_filename(original: str) -> str:
    if not original:
        return "document.pdf"
    base, _ = os.path.splitext(original)
    return f"{base}.pdf" if base else "document.pdf"


@app.post("/upload")
async def upload_file(
    file: UploadFile
):
    content_type = file.content_type or ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only PDF or Word (.docx) resumes are allowed.",
        )
    name = (file.filename or "").lower()
    if not name.endswith(".pdf") and not name.endswith(".docx"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF or Word (.docx) resumes are allowed.",
        )

    db_file = await files_collection.insert_one(
        document=FileSchema(name=file.filename, status="saving")
    )
    file_id = str(db_file.inserted_id)
    file_bytes = await file.read()

    # Convert Word to PDF if needed; then store PDF in GridFS
    if content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or name.endswith(".docx"):
        loop = asyncio.get_event_loop()
        file_bytes = await loop.run_in_executor(None, docx_to_pdf, file_bytes)
        store_filename = _pdf_filename(file.filename or "")
    else:
        store_filename = file.filename or "document.pdf"

    loop = asyncio.get_event_loop()
    gridfs_id = await loop.run_in_executor(
        None, lambda: put_file(file_bytes, store_filename)
    )

    q.enqueue(process_file_job, file_id, str(gridfs_id))

    await files_collection.update_one(
        {"_id": db_file.inserted_id},
        {"$set": {"status": "queued"}},
    )

    return {"file_id": file_id}
