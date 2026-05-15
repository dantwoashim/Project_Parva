---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Frontend Architecture

Status: Phase 09 developer-experience baseline.

The frontend is capability-aware. Route visibility is controlled by the route profile and capability map, not by ad hoc page checks.

## Capability map

Canonical capability files:

- `frontend/src/config/routeCapabilities.js`
- `frontend/src/config/capabilityMap.js`
- `frontend/src/navigation/routeManifest.js`
- `frontend/src/hooks/useBackendCapabilities.js`

Public profiles must not expose private future-BS exact output, private data, or research-private routes. The active guard is tested in `frontend/src/test/CapabilityGating.test.jsx`.

## Large component extraction

`frontend/src/redesign/ParvaExperience.jsx` is still the largest shell. Phase 09
keeps the extraction path measurable instead of rewriting the UI in one risky
pass. Existing reusable verification UI already lives in:

```text
frontend/src/redesign/components/VerificationComponents.jsx
```

The extraction is covered by:

```text
frontend/src/test/VerificationComponents.test.jsx
```

Growth is checked by:

```bash
python scripts/frontend/check_component_size.py --max-lines 800 --warn-only
```

Current priority extraction targets are route shells, capability/status badges,
source/evidence/confidence badges, research warning panels, festival cards, and
trust/protocol sections.

## Typed API models

Frontend API response shapes live in:

```text
frontend/src/types/api.ts
```

The models preserve maturity lane, source metadata, claim boundary, trace id, and public capability metadata so UI code can show uncertainty and avoid official-authority language.

## Embed surfaces

Static embeds live under:

```text
frontend/public/embed/
```

The loader and plain iframe mode both support `api_base` configuration. See `docs/EMBED_GUIDE.md`.

## Verification commands

```bash
npm --prefix frontend run lint
npm --prefix frontend run build
npm --prefix frontend test -- --run
python scripts/frontend/check_component_size.py --max-lines 800 --warn-only
```
