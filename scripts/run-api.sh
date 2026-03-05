#!/bin/bash
set -euo pipefail
# Use PORT from environment (e.g. Railway) or default 8000
uvicorn app.server:app --host 0.0.0.0 --port "${PORT:-8000}"
