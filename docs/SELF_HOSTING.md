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
python3.11 -m pip install -e packages/parva-python
uvicorn app.main:app --app-dir backend --reload --port 8000
```

## Docker

Build:

```bash
docker build -t project-parva .
```

The default Docker build does not fetch the JPL DE440 kernel from NASA during
image construction. That keeps a fresh public clone reproducible without a live
third-party download. If you need live JPL-backed regeneration inside the image,
opt in explicitly:

```bash
docker build \
  --build-arg PARVA_DOWNLOAD_JPL_KERNEL=1 \
  --build-arg PARVA_JPL_DE440_MD5=c9d581bfd84209dbeee8b1583939b148 \
  -t project-parva .
```

The download script verifies the kernel checksum before storing it. Deployments
can also mount a preverified `.bsp` file and set `PARVA_JPL_DE440_KERNEL` to
that path.

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

## Cloud Run backend-only container

For split hosting, use the backend-only container instead of the combined Render-oriented image:

```bash
docker build -f Dockerfile.cloudrun -t project-parva-cloudrun .
docker run --rm -p 8080:8080 \
  -e PORT=8080 \
  -e PARVA_ENV=production \
  -e PARVA_SERVE_FRONTEND=false \
  -e PARVA_SOURCE_URL=https://github.com/example/project-parva \
  -e PARVA_RATE_LIMIT_BACKEND=redis \
  -e PARVA_REDIS_URL=rediss://default:<password>@example.upstash.io:6379 \
  -e PARVA_REQUIRE_PRECOMPUTED=false \
  -e PARVA_PLACE_SEARCH_ALLOW_REMOTE=false \
  -e PARVA_PLACE_SEARCH_PROVIDER_CHAIN=offline \
  -e PARVA_PLACE_SEARCH_PROVIDER_POLICY=offline_only \
  project-parva-cloudrun
```

For Cloud Run builds that require JPL-backed precompute, pass both
`PARVA_DOWNLOAD_JPL_KERNEL=1` and `PARVA_PRECOMPUTE=1` at build time. Without
those build args, the container remains backend-only and serves public runtime
surfaces from checked-in public artifacts and runtime computation.

That image is intended for Cloud Run or another container host where the frontend is published separately on a static host such as Cloudflare Pages.

## Frontend

The frontend is built separately with Vite and served by FastAPI when `PARVA_SERVE_FRONTEND=true` and a local production build has been generated under `frontend/`.

## Hosted service requirements

- publish corresponding source
- document your own operational policies
- review [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)
- do not present experimental tracks as stable hosted contracts
