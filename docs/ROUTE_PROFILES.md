---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Route Profiles

Status: route exposure control.

Source of truth: [config/route-maturity.yaml](../config/route-maturity.yaml)

Route profiles control which FastAPI routers are mounted and which OpenAPI
documents are safe to publish.

## Profiles

| Profile | Public | Research private allowed | Intended use |
| --- | --- | --- | --- |
| `minimal_public` | Yes | No | Health, policy, and metadata-only checks. |
| `public_demo` | Yes | No | Lightweight public demo with core calendar and public-safe previews. |
| `public_reference` | Yes | No | Public reference API without private research outputs. |
| `developer_preview` | Yes | No | Public developer preview for draft and preview APIs. |
| `enterprise_preview` | No | No | Controlled enterprise, billing, and admin-adjacent workflows. |
| `research_private` | No | Yes | Controlled future-BS research routes and exact outputs. |
| `internal_lab` | No | Yes | Internal raw-source, calibration, and model-risk work. |
| `full_dev` | No | Yes | Local integration profile with all warnings visible. |

## Public Profile Rules

Public profiles must not expose:

- `/v4/api/future-bs/{prediction,range,export,backtest,residuals,explain,boundary,model-runs,loan-impact}`
- `/v5/api/calendar-model-risk/{prediction,ranges,validation,calibration,residuals,boundary,model-runs,sheets}`
- private model internals
- generated future vectors
- private source paths or private artifacts
- billing, API-key, webhook, or admin mutation routes

Public profiles may expose only the future-BS and calendar-model-risk
capability summaries. Those responses describe method, risk labels, claim
boundaries, and warnings, not exact future BS values.

## OpenAPI Artifacts

The checked-in public profile specs are:

| Profile | File |
| --- | --- |
| `public_reference` | `docs/api-docs/openapi.public-reference.json` |
| `developer_preview` | `docs/api-docs/openapi.developer-preview.json` |
| `enterprise_preview` | `docs/api-docs/openapi.enterprise-preview.json` |

Regenerate them with:

```bash
python scripts/release/generate_openapi_profiles.py
```

Check all public OpenAPI mirrors with:

```bash
python scripts/release/check_openapi_drift.py
```

## SDK Exposure Policy

SDKs may keep stable calendar helpers at the top level. Preview and draft
methods must be documented with maturity labels, and research-private exact
future routes must not be presented as stable SDK methods.

Existing compatibility aliases remain documented, but new SDK work should group
preview and draft helpers under explicit preview or draft namespaces.

