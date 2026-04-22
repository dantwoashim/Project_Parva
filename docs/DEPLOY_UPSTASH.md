# Deploy with Upstash Redis

Use Upstash Redis for distributed rate limiting and lightweight shared cache state. Do not rely on in-process memory for a multi-instance hosted backend.

## What to store in Upstash

- rate-limit counters
- small cache entries
- lightweight coordination state

Do not treat Upstash as the primary long-term store for large artifacts or source data.

## Connection details

Use the TLS URL from Upstash:

- `PARVA_REDIS_URL=rediss://...`

Do not use a plain `redis://` URL unless you explicitly know your provider path is safe and intended for non-TLS traffic.

## Backend settings

Set:

- `PARVA_RATE_LIMIT_ENABLED=true`
- `PARVA_RATE_LIMIT_BACKEND=redis`
- `PARVA_REDIS_URL=<your Upstash rediss:// URL>`

## Operational note

If you lock Down access or rotate credentials, update the Cloud Run service environment immediately and verify `/health/ready` plus one public `/v3/api/*` request afterward.
