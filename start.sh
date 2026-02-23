#!/usr/bin/env bash
# start.sh — Build frontend and serve the full app via uvicorn.
#
# In production mode, FastAPI serves the React build from frontend/dist/
# alongside the API on a single port (8000). No separate frontend server needed.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
NODE_DIR="/usr/local/Cellar/node/25.2.1/bin"
VENV_PYTHON="$REPO_ROOT/.venv/bin/python"

echo "=== Building frontend ==="
cd "$REPO_ROOT/frontend"
PATH="$NODE_DIR:/bin:/usr/bin:$PATH" npm install --silent
PATH="$NODE_DIR:/bin:/usr/bin:$PATH" npm run build

echo ""
echo "=== Starting backend (port 8000) ==="
cd "$REPO_ROOT/backend"
exec "$VENV_PYTHON" -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
