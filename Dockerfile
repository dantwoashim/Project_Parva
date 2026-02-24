FROM node:20-alpine AS frontend-builder
WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend ./
ARG VITE_API_BASE=/v3/api
ENV VITE_API_BASE=${VITE_API_BASE}
RUN npm run build


FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=backend \
    PARVA_SERVE_FRONTEND=true \
    PARVA_ENABLE_EXPERIMENTAL_API=false \
    PARVA_ENV=production

COPY pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir fastapi uvicorn pydantic pyswisseph aiohttp

COPY backend /app/backend
COPY data /app/data
COPY output/precomputed /app/output/precomputed
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "backend"]
