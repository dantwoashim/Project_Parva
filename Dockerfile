FROM node:20.19.0-alpine3.20 AS frontend-builder
WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend ./
ARG VITE_API_BASE=/v3/api
ENV VITE_API_BASE=${VITE_API_BASE}
RUN npm run build


FROM python:3.11.11-slim-bookworm
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=backend \
    PATH="/opt/venv/bin:$PATH" \
    PARVA_SERVE_FRONTEND=true \
    PARVA_ENABLE_EXPERIMENTAL_API=false \
    PARVA_RATE_LIMIT_ENABLED=true \
    PARVA_ENV=production

RUN python -m venv /opt/venv

COPY LICENSE README.md pyproject.toml /app/
COPY requirements/constraints.txt /app/requirements/constraints.txt
COPY backend /app/backend
COPY scripts /app/scripts
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -c requirements/constraints.txt -e .

COPY data /app/data
RUN mkdir -p /app/output/precomputed \
    && START_YEAR="$(date -u +%Y)" \
    && END_YEAR="$((START_YEAR + 2))" \
    && python /app/scripts/precompute/precompute_all.py \
        --start-year "${START_YEAR}" \
        --end-year "${END_YEAR}"
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

RUN useradd --create-home --shell /usr/sbin/nologin parva \
    && chown -R parva:parva /app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import json, sys, urllib.request; r = urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=5); payload = json.loads(r.read().decode()); sys.exit(0 if r.status == 200 and payload.get('status') == 'ready' else 1)"

USER parva
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "backend"]
