FROM node:20.20.2-alpine3.22 AS frontend-builder
WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend ./
ARG VITE_API_BASE=/v3/api
ENV VITE_API_BASE=${VITE_API_BASE}
RUN npm run build


FROM python:3.11.11-slim-bookworm
WORKDIR /app

ARG PARVA_DOWNLOAD_JPL_KERNEL=0
ARG PARVA_JPL_DE440_MD5=c9d581bfd84209dbeee8b1583939b148
ARG PARVA_PRECOMPUTE=0
ARG PARVA_PRECOMPUTE_START_YEAR
ARG PARVA_PRECOMPUTE_END_YEAR

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=backend \
    PATH="/opt/venv/bin:$PATH" \
    PARVA_SERVE_FRONTEND=true \
    PARVA_ENABLE_EXPERIMENTAL_API=false \
    PARVA_RATE_LIMIT_ENABLED=true \
    PARVA_RATE_LIMIT_BACKEND=memory \
    PARVA_REQUIRE_PRECOMPUTED=false \
    PARVA_JPL_DE440_KERNEL=/app/data/ephemeris/jpl/de440.bsp \
    PARVA_ENV=public

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv

COPY LICENSE README.md pyproject.toml /app/
COPY requirements/constraints.txt /app/requirements/constraints.txt
COPY backend /app/backend
COPY scripts /app/scripts
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -c requirements/constraints.txt -e .

COPY data /app/data
RUN mkdir -p /app/data/ephemeris/jpl \
    && if [ "$PARVA_DOWNLOAD_JPL_KERNEL" = "1" ]; then \
         python /app/scripts/download_jpl_kernel.py \
           --kernel de440 \
           --md5 "$PARVA_JPL_DE440_MD5" \
           --output /app/data/ephemeris/jpl/de440.bsp \
           --quiet; \
       else \
         echo "Skipping JPL kernel download. Set PARVA_DOWNLOAD_JPL_KERNEL=1 to fetch and checksum-verify de440.bsp during build."; \
       fi
RUN mkdir -p /app/output/precomputed \
    && if [ "$PARVA_PRECOMPUTE" = "1" ]; then \
         if [ -z "$PARVA_PRECOMPUTE_START_YEAR" ] || [ -z "$PARVA_PRECOMPUTE_END_YEAR" ]; then \
           echo "PARVA_PRECOMPUTE_START_YEAR and PARVA_PRECOMPUTE_END_YEAR are required when PARVA_PRECOMPUTE=1"; \
           exit 1; \
         fi; \
         python /app/scripts/precompute/precompute_all.py \
           --start-year "${PARVA_PRECOMPUTE_START_YEAR}" \
           --end-year "${PARVA_PRECOMPUTE_END_YEAR}"; \
       else \
         echo "Skipping build-time precompute. Generate release artifacts explicitly or set PARVA_PRECOMPUTE=1 with explicit year args."; \
       fi
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

RUN useradd --create-home --shell /usr/sbin/nologin parva \
    && chown -R parva:parva /app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import json, sys, urllib.request; r = urllib.request.urlopen('http://127.0.0.1:8000/health/ready', timeout=5); payload = json.loads(r.read().decode()); sys.exit(0 if r.status == 200 and payload.get('status') == 'ready' else 1)"

USER parva
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "backend"]
