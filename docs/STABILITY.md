# Stability Guide

Project Parva has one canonical public API track and several supporting surfaces with different maturity levels.

## Stability levels

| Level | Meaning |
| --- | --- |
| Stable public contract | Backwards-compatible surface intended for integrations |
| Public beta | Publicly usable, but still evolving in UX, operational maturity, or editorial completeness |
| Experimental | Disabled by default or explicitly not contract-stable |
| Legacy compatibility | Still shipped for old clients, but not recommended for new work |

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

## Guidance

- New integrations should target `/v3/api/*`.
- Do not treat `/api/*` as future-proof.
- Do not market experimental or lab surfaces as authoritative core product behavior.
- If you expose Parva outputs to end users, keep [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) visible.
