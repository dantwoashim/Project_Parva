# Self-Hosting

Project Parva can be self-hosted locally or in a small deployment, but the public repo assumes you are responsible for your own operations, rate limiting, and source publication.

## Local development

```bash
make install
make dev-backend
make dev-frontend
```

## Local backend only

```bash
python3.11 -m pip install -e .[test,dev]
python3.11 -m pip install -e sdk/python
uvicorn app.main:app --app-dir backend --reload --port 8000
```

## Docker

Build:

```bash
docker build -t project-parva .
```

Run a low-friction local container:

```bash
docker run --rm -p 8000:8000 \
  -e PARVA_ENV=development \
  -e PARVA_SOURCE_URL=https://github.com/example/project-parva \
  project-parva
```

For a real production deployment, provide:

- `PARVA_ENV=production`
- `PARVA_SOURCE_URL=<public repo or exact source archive>`
- `PARVA_RATE_LIMIT_BACKEND=redis`
- `PARVA_REDIS_URL=<your redis connection string>`

## Frontend

The frontend is built separately with Vite and served by FastAPI when `PARVA_SERVE_FRONTEND=true` and a local production build has been generated under `frontend/`.

## Hosted service requirements

- publish corresponding source
- document your own operational policies
- review [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)
- do not present experimental tracks as stable hosted contracts
