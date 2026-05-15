---
status: stable
audience: sdk
---

# SDK Strategy

Project Parva has two canonical SDK packages:

| Package | Status | Role |
| --- | --- | --- |
| `packages/parva-python` | canonical alpha | Python SDK for public v3 APIs and safe capability summaries. |
| `packages/parva-js` | canonical alpha | JavaScript/TypeScript SDK for public v3 APIs and safe capability summaries. |
| `sdk/python` | compatibility scaffold | Deprecated compatibility path. New work should target `packages/parva-python`. |

## Stable Surface

Stable top-level SDK helpers should stay focused on:

- current Nepali calendar context,
- AD/BS conversion,
- BS date validation,
- fiscal-year lookup,
- BS month metadata,
- working-day and compliance decision support,
- public trust/source metadata,
- public capability summaries.

Preview or draft helper families must remain labeled in README files and
release notes. Exact Future-BS predictions, private source audit, model-run
internals, export routes, loan-impact simulations, admin routes, billing
routes, trust mutation routes, and private route tokens must not be SDK default
surface.

## Version Boundary

- `v3` is the canonical stable/core API.
- `v4` is preview/research-private where applicable; public Future-BS exposure
  is capability metadata only.
- `v5` is model-risk/research or explicit preview.
- `v2` and `/api/*` compatibility aliases are deprecated.

## Adoption Rule

A developer should be able to install an SDK, call conversion, validate dates,
inspect review boundaries, and run public verification in under ten minutes
without learning private research routes.
