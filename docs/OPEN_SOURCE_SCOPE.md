# Open Source Scope

This repository is the public open-source core of Project Parva.

## Included in the open-source core

- the FastAPI backend and public API routes
- the reference frontend
- the Python SDK
- public docs, tests, and release scripts
- data files that are required for the public runtime or public evidence workflow

## Experimental but still public

- `/v2`, `/v4`, `/v5` alias tracks when explicitly enabled
- lab and exploratory frontend surfaces
- proof-of-concept integrations such as the Telegram bot script
- design/reference stitch artifacts

These are public, but they are not part of the stable compatibility promise.

## Legacy compatibility

- `/api/*` remains public for compatibility with older clients and the current hosted app
- it should not be the basis for new integrations

## Better kept private or moved later

- raw third-party archival material with redistribution or token-review risk
- production-only operational runbooks and credentials
- hosted-service analytics, billing, and support operations
- any future admin consoles or commercial-only overlays that are not needed for the open-source core
