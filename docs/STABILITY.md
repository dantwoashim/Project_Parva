# Stability Guide

Status: Phase 04 stability and deprecation labels.

Project Parva has one canonical public API track and several supporting surfaces with different maturity levels.

## Stability levels

| Level | Meaning |
| --- | --- |
| Stable public contract | Backwards-compatible surface intended for integrations |
| Public beta | Publicly usable, but still evolving in UX, operational maturity, or editorial completeness |
| Experimental | Disabled by default or explicitly not contract-stable |
| Legacy compatibility | Still shipped for old clients, but not recommended for new work |

The machine-readable lane source is
[config/subsystem-maturity.yaml](../config/subsystem-maturity.yaml). Route
profile exposure is controlled by
[config/route-maturity.yaml](../config/route-maturity.yaml).

## Current map

| Surface | Level | Notes |
| --- | --- | --- |
| `/v3/api/*` | Stable public contract | Canonical public API track |
| Python SDK | Stable public-beta | Built from artifacts and validated in release gates |
| Reference frontend | Public beta | Useful and maintained, but still a reference product |
| ICS feeds and widgets | Public beta | Publicly usable, still evolving operationally |
| `/api/*` | Legacy compatibility | Existing clients only |
| `/v2`, `/v4`, `/v5` | Experimental | Disabled by default and not isolated versions |
| Labs and PoCs | Experimental | Not part of the compatibility promise |

## Phase 04 Lanes

| Lane | Stability promise |
| --- | --- |
| `stable_core` | Backwards-compatible public core subject to release gates. |
| `public_preview` | Public-safe but may change. Requires clear labels and metadata. |
| `developer_preview` | Public developer preview. Contract details may change. |
| `enterprise_preview` | Controlled enterprise preview, not public-demo default. |
| `research_private` | Private by default. No public exact outputs. |
| `protocol_draft` | Draft protocol work, not a standard or certification. |
| `deprecated_compatibility` | Legacy alias with sunset policy. |
| `historical` | Historical docs only, not current verification status. |

## Deprecation Policy

`/v3/api/*` is the canonical public API track. `/api/*` compatibility aliases
remain available for existing clients, but new integrations should use `/v3`.
Compatibility aliases must include deprecation metadata or headers where the
runtime supports them.

## Guidance

- New integrations should target `/v3/api/*`.
- Do not treat `/api/*` as future-proof.
- Do not market experimental or lab surfaces as authoritative core product behavior.
- If you expose Parva outputs to end users, keep [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) visible.
