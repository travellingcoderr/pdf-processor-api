# Deploying to Railway

Use **three services**: Backend (API), Worker, Frontend. Each service can use a **Dockerfile** or Railway’s Nixpacks; set **Root Directory** and **Start Command** as below.

---

## Backend (API)

| Setting | Value |
|--------|--------|
| **Root Directory** | *(repo root)* |
| **Dockerfile path** | `backend/Dockerfile` |
| **Start Command** | `./run-api.sh` or `uvicorn app.server:app --host 0.0.0.0 --port ${PORT:-8000}` |

Build context is repo root (so the Dockerfile can `COPY backend/...` and `scripts/...`). The API listens on the port Railway sets via `PORT` (or 8000 if unset).

---

## Worker

| Setting | Value |
|--------|--------|
| **Root Directory** | *(repo root)* |
| **Dockerfile path** | `worker/Dockerfile` |
| **Start Command** | `./run-worker.sh` or `python -m app.worker` |

Build context is repo root (so the Dockerfile can `COPY backend/...` and `scripts/...`).

---

## Frontend

| Setting | Value |
|--------|--------|
| **Root Directory** | *(leave empty = repo root)* — the Dockerfile expects context = repo root and copies `frontend/`. |
| **Dockerfile path** | `frontend/Dockerfile` (set via `frontend/railway.toml` or **RAILWAY_DOCKERFILE_PATH** = `frontend/Dockerfile`) |
| **Start Command** | *(leave default)* — the image runs `nginx` to serve the built static files. |

The frontend Dockerfile is written for **build context = repo root** (so `COPY frontend/...` works). In the frontend service: set **Root Directory** to empty (repo root), and in **Settings** set **Config file path** to `frontend/railway.toml` so Railway uses `builder = "DOCKERFILE"` and `dockerfilePath = "frontend/Dockerfile"`.

---

## Summary

| Service  | Root Directory | Dockerfile           | Start Command   |
|----------|----------------|----------------------|-----------------|
| Backend  | *(root)*       | `backend/Dockerfile` | `./run-api.sh`  |
| Worker   | *(root)*       | `worker/Dockerfile`  | `./run-worker.sh` |
| Frontend | *(root)*       | `frontend/Dockerfile` | *(default)*     |

**Note:** Backend and Worker both use **repo root** as build context so they can use shared `scripts/` and `backend/` code.
