FROM node:22-alpine AS web
WORKDIR /build
COPY web/package*.json ./
RUN npm ci
COPY web/ .
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src/ src/
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev \
    && pip install --no-cache-dir .[api] \
    && apt-get purge -y --auto-remove gcc libc6-dev && rm -rf /var/lib/apt/lists/*
COPY --from=web /build/dist web/dist
ENV PARVA_WEB_DIST=/app/web/dist
EXPOSE 8080
USER 10001:10001
CMD ["uvicorn", "parva.api:app", "--host", "0.0.0.0", "--port", "8080"]
