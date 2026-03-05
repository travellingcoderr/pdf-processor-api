# Worker image: same Python deps and app code as backend, runs RQ worker.
# Build from repo root: docker build -f worker/Dockerfile .
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends poppler-utils gcc && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY scripts/run-worker.sh ./run-worker.sh

RUN chmod +x /app/run-worker.sh && mkdir -p /mnt/uploads

CMD ["./run-worker.sh"]
