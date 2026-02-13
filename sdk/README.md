# Project Parva SDKs (Authority Track)

This folder contains productionized SDKs:
- `sdk/python/parva_sdk` (Python, typed envelope + retry/backoff)
- `sdk/typescript/src` (TypeScript, typed envelope + retry/backoff)
- `sdk/go/parva` (Go, typed envelope + retry/backoff)

Default contract target:
- `/v5/api` authority-track envelope (`data` + `meta`)
- v3 compatibility fallback when consuming legacy payloads

Each SDK now includes packaging metadata (`pyproject.toml`, `package.json`, `go.mod`)
to support publication workflows.
