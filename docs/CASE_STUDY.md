# Case Study: Project Parva

## Summary

Project Parva is a Nepal-focused temporal API platform for BS/AD conversion, panchanga data, festival timing, widgets, feeds, and developer-facing SDK/docs.

## Problem

Nepali calendar and festival dates are not just date lookups. They depend on calendar systems, lunar timing, local observance rules, source confidence, and tradition-specific interpretation. Static calendar apps often hide those details.

## Why this project matters

Parva shows how a culturally specific domain can be modeled as a documented API rather than a loose set of hard-coded dates.

## My role

I designed and implemented the backend/API surface, documentation posture, validation notes, SDK support, and the reference frontend.

## Tech stack

- Backend: Python, FastAPI, Pydantic, pyswisseph
- Data/cache: curated calendar data, Redis-aware cache/rate-limit paths
- Frontend: React/Vite reference app
- Testing: Pytest, API smoke tests, SDK validation
- Tooling: GitHub Actions, Makefile, release/hygiene scripts

## Architecture

The FastAPI backend exposes the canonical `/v3/api/*` contract. Domain modules handle calendar conversion, panchanga calculations, festival lookup, public artifacts, and integration docs. The frontend and widgets consume the API as reference clients rather than defining the source of truth.

```text
Frontend/widgets/SDK -> FastAPI v3 routes -> calendar + panchanga services -> data/source inventories
                                      -> optional Redis/cache/rate-limit support
```

## Key features

- BS/AD conversion within a documented support range
- Panchanga and festival endpoints
- Developer portal, OpenAPI docs, embed examples, and Python SDK
- Stability notes for stable, legacy, and experimental API surfaces
- Accuracy and known-limit documentation

## Hard technical problems

- Keeping stable API behavior separate from experimental aliases
- Explaining festival accuracy without pretending to be an official authority
- Combining computed astronomical values with curated source inventories
- Testing date and festival edge cases that are easy to misunderstand manually

## Important decisions and tradeoffs

- Treat `/v3/api/*` as the canonical public contract.
- Keep `/api/*` as legacy compatibility.
- Mark `/v2`, `/v4`, `/v5`, labs, and PoCs as experimental unless explicitly stabilized.
- Prefer documented limitations over false confidence for religious/cultural timing.

## Testing and validation

The project uses Pytest for backend and calendar behavior, SDK packaging validation, and CI checks. Validation is supported by source inventories and public limitation docs rather than a single unqualified "correct" answer.

## Security and limitations

This is not an official government calendar, legal authority, or universal doctrinal source. Caching and rate-limiting paths should be configured carefully in hosted environments.

## What I learned

- API versioning and compatibility management
- Domain modeling for culturally specific date systems
- Documentation as a product surface
- Testing around edge cases and source ambiguity

## What I would improve with more time

- Add more public source comparison tables
- Improve observability for hosted API usage
- Add more SDK examples and generated clients
- Expand test fixtures for regional observance profiles

## What this project proves to employers

Parva proves I can build a non-trivial API product with domain complexity, explicit contracts, tests, docs, deployment thinking, and honest limitations.

## Resume bullets

- Built a FastAPI-based Nepal temporal API with BS/AD conversion, panchanga/festival endpoints, developer docs, a Python SDK, and tests for calendar-related edge cases.
- Designed a public API versioning posture that separates stable `/v3/api/*` endpoints from legacy and experimental surfaces.
- Documented accuracy boundaries, validation sources, and limitations for festival and astronomical calculations to avoid overclaiming authority.

