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
| **Root Directory** | `frontend` |
| **Start Command** | *(leave default)* — the frontend Dockerfile runs `nginx` to serve the built static files. |

The repo includes `frontend/railway.json` so Railway uses the **Dockerfile** builder instead of Railpack (avoids "Error creating build plan with Railpack" in monorepos).  
If you use the Dockerfile (recommended), you don’t need a custom start command.  
If you use a **Node buildpack** instead of Docker, use: `npm run build && npx serve -s dist -l ${PORT:-3000}` (and set build command to `npm install && npm run build`).

---

## Summary

| Service  | Root Directory | Dockerfile           | Start Command   |
|----------|----------------|----------------------|-----------------|
| Backend  | *(root)*       | `backend/Dockerfile` | `./run-api.sh`  |
| Worker   | *(root)*       | `worker/Dockerfile`  | `./run-worker.sh` |
| Frontend | `frontend`     | `Dockerfile`         | *(default)*     |

**Note:** Backend and Worker both use **repo root** as build context so they can use shared `scripts/` and `backend/` code.
