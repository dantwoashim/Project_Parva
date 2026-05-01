#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON:-}"
if [[ -z "$PYTHON_BIN" ]]; then
  if [[ -x ".venv/bin/python" ]]; then
    PYTHON_BIN=".venv/bin/python"
  elif command -v python3.11 >/dev/null 2>&1; then
    PYTHON_BIN="python3.11"
  else
    PYTHON_BIN="python3"
  fi
fi

if [[ ! -f "frontend/dist/index.html" ]]; then
  cat >&2 <<'EOF'
frontend/dist/index.html is missing.

Build the frontend first:

  make build-frontend

Then rerun:

  make dev-local
EOF
  exit 1
fi

export PARVA_SERVE_FRONTEND="${PARVA_SERVE_FRONTEND:-true}"
export PARVA_ENV="${PARVA_ENV:-development}"
export PARVA_RATE_LIMIT_BACKEND="${PARVA_RATE_LIMIT_BACKEND:-memory}"
export PYTHONPATH="${PYTHONPATH:-backend}"

HOST="${PARVA_LOCAL_HOST:-127.0.0.1}"
PORT="${PARVA_LOCAL_PORT:-8000}"

echo "Starting Parva same-origin local review server..."
echo "  URL: http://${HOST}:${PORT}/today"
echo "  API: http://${HOST}:${PORT}/v3/api"
echo "  Frontend: frontend/dist"

exec "$PYTHON_BIN" -m uvicorn app.main:app --host "$HOST" --port "$PORT" --app-dir backend
