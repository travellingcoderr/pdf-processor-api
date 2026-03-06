# Build from repo root: docker build -f backend/Dockerfile .
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        libreoffice \
        poppler-utils \
        gcc && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY scripts/run-api.sh ./run-api.sh
COPY scripts/run-worker.sh ./run-worker.sh

RUN chmod +x /app/run-api.sh /app/run-worker.sh && mkdir -p /mnt/uploads

EXPOSE 8000
CMD ["./run-api.sh"]
