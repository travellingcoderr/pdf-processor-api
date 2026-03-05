import asyncio
import base64
import os

from bson import ObjectId
from openai import OpenAI
from pdf2image import convert_from_path

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


def process_file_job(file_id: str, file_path: str) -> None:
    """RQ-compatible sync entrypoint.

    RQ workers call normal Python functions. This wrapper starts an event loop and
    runs the async Mongo/document pipeline inside it.
    """
    asyncio.run(_process_file_async(file_id, file_path))
