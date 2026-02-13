# SDK Usage (Authority Track Update)

## Python
Location:
- `/Users/rohanbasnet14/Documents/Project Parva/sdk/python/parva_sdk`
- Packaging:
  - `/Users/rohanbasnet14/Documents/Project Parva/sdk/python/pyproject.toml`

Core methods:
- `today()`
- `convert(date)`
- `panchanga(date)`
- `upcoming(days)`
- `observances(date, location, preferences)`
- `next_observance(...)`
- `resolve(date, profile, latitude, longitude, include_trace)`
- `spec_conformance()`
- `verify_trace(trace_id)`

Behavior:
- Returns typed `DataEnvelope` (`data` + `meta`) for v5 endpoints.
- Includes retry/backoff and v3 compatibility fallback.

## TypeScript
Location:
- `/Users/rohanbasnet14/Documents/Project Parva/sdk/typescript/src/index.ts`
- Packaging:
  - `/Users/rohanbasnet14/Documents/Project Parva/sdk/typescript/package.json`
  - `/Users/rohanbasnet14/Documents/Project Parva/sdk/typescript/tsconfig.json`

Core methods:
- `today()`
- `convert(date)`
- `panchanga(date?)`
- `upcoming(days)`
- `observances(date, location, preferences)`
- `resolve(date, options?)`
- `specConformance()`
- `verifyTrace(traceId)`

## Go
Location:
- `/Users/rohanbasnet14/Documents/Project Parva/sdk/go/parva/client.go`
- Packaging:
  - `/Users/rohanbasnet14/Documents/Project Parva/sdk/go/go.mod`

Core methods:
- `Today()`
- `Convert(date)`
- `Panchanga(date)`
- `Upcoming(days)`
- `ExplainFestival(id, year)`
- `ExplainTrace(traceID)`
- `Resolve(date, profile, lat, lon, includeTrace)`
- `SpecConformance()`
- `VerifyTrace(traceID)`

## Contract Notes
All SDKs currently target:
- Base path: `/v5/api` (authority track)
- v3 compatibility fallback for legacy responses
- Typed envelope metadata (`confidence`, `method`, `provenance`, `uncertainty`, `trace_id`, `policy`)
