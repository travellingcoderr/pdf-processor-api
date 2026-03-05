#!/bin/bash
set -euo pipefail
# No --reload here to avoid Docker/mounted-volume file system issues.
uvicorn app.server:app --host 0.0.0.0 --port 8000
