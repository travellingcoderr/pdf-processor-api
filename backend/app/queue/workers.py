import asyncio
import base64
import logging
import os

from bson import ObjectId

logger = logging.getLogger(__name__)
from openai import OpenAI
from pdf2image import convert_from_path

# Worker writes images under UPLOAD_ROOT; on Railway set UPLOAD_ROOT=/tmp (no shared disk)
from app.config import OPENAI_API_KEY, OPENAI_MODEL, UPLOAD_ROOT
from app.db.collections.files import files_collection

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def _process_file_async(file_id: str, file_path: str) -> None:
    await files_collection.update_one(
        {"_id": ObjectId(file_id)},
        {"$set": {"status": "processing"}},
    )

    try:
        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {"status": "converting_to_images"}},
        )

        pages = convert_from_path(file_path)
        images: list[str] = []

        for i, page in enumerate(pages):
            image_save_path = f"{UPLOAD_ROOT}/images/{file_id}/image-{i}.jpg"
            os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
            page.save(image_save_path, "JPEG")
            images.append(image_save_path)

        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {"status": "images_ready"}},
        )

        if not images:
            raise RuntimeError("No images were produced from the PDF")
        if client is None:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        first_image = encode_image(images[0])
        result = client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Based on the resume below, roast this resume."},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{first_image}",
                        },
                    ],
                }
            ],
        )

        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {"status": "processed", "result": result.output_text}},
        )
    except Exception as exc:
        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {"status": "failed", "result": str(exc)}},
        )
        raise


def process_file_job(file_id: str, gridfs_file_id: str) -> None:
    """RQ-compatible sync entrypoint.

    Reads PDF from GridFS (so worker can run in a different container than the API),
    writes to a temp file, then runs the async pipeline.
    """
    import tempfile

    from app.db.gridfs_store import get_file

    logger.info("Job started: file_id=%s", file_id)
    try:
        data = get_file(gridfs_file_id)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        try:
            asyncio.run(_process_file_async(file_id, tmp_path))
            logger.info("Job finished: file_id=%s", file_id)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
    except Exception as exc:
        logger.exception("Job failed: file_id=%s error=%s", file_id, exc)
        raise
