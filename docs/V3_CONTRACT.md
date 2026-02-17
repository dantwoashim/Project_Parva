# API v3 Contract Specification (M35)

## Version: 3.0 LTS (Long-Term Stable)

This document freezes the v3 API contract. No breaking changes will be made. New fields may be added but existing fields will not be removed or have their types changed.

## LTS Guarantees

- v3 endpoints will remain stable for **minimum 24 months** after publication
- Deprecation requires **6-month advance notice** via `Sunset` HTTP header
- All SDKs (Python, JS, Go) will maintain v3 parity

## Migration from v2 → v3

### Breaking Changes
| v2 Field | v3 Field | Change |
|----------|----------|--------|
| `provenance` (flat) | `meta.provenance` (nested) | Moved into `meta` block |
| No `trace_id` | `meta.calculation_trace_id` | Added (always present) |
| No `uncertainty` | `meta.uncertainty` | Added (always present) |
| No `explain` | `meta.explain.trace_id` | Added (always present) |
| `confidence` in `tithi` | `meta.confidence` | Moved to top-level meta |

### Non-Breaking Additions
- `meta.provenance.verify_url` — verification link
- `meta.provenance.snapshot_id` — quarterly snapshot identifier
- `observance_variants[]` — regional variant array (when applicable)

## Mandatory Response Shape (v3 Final)

```json
{
  "data": { "..." },
  "meta": {
    "confidence": "official|estimated|computed",
    "method": "ephemeris_udaya|synodic|lookup|override",
    "calculation_trace_id": "tr_abc123def456",
    "provenance": {
      "snapshot_id": "snap_2028Q4",
      "dataset_hash": "sha256:a1b2c3...",
      "rules_hash": "sha256:d4e5f6...",
      "merkle_root": "abc123...",
      "verify_url": "https://parva.dev/verify/tr_abc123def456"
    },
    "uncertainty": {
      "level": "low|medium|high",
      "interval_hours": 0.5
    },
    "explain": {
      "trace_id": "tr_abc123def456"
    }
  },
  "engine_version": "v3"
}
```

## Endpoint Freeze List

All endpoints under `/api/calendar/*`, `/api/engine/*`, `/api/webhooks/*` are frozen. Paths, methods, and response shapes will not change.

## SDK Parity Matrix

| Feature | Python SDK | JS SDK | Go SDK |
|---------|-----------|--------|--------|
| Convert date | ✅ | ✅ | ✅ |
| Today | ✅ | ✅ | ✅ |
| Panchanga | ✅ | ✅ | ✅ |
| Festival calculate | ✅ | ✅ | ✅ |
| Upcoming festivals | ✅ | ✅ | ✅ |
| Cross-calendar | ✅ | ✅ | ✅ |
| Explain | ✅ | ✅ | ✅ |
| Forecast | ✅ | ✅ | ✅ |
| Engine health | ✅ | ✅ | ✅ |
| iCal feed | ✅ | ✅ | ✅ |

## Hard Deprecations

| Deprecated | Replacement | Removal Date |
|------------|-------------|-------------|
| `/api/calendar/convert` (flat provenance) | Same endpoint with `meta` block | v3 launch |
| Legacy calculator V1 | V2 engine (sole path) | v3 launch |
| `confidence` inside `tithi` object | `meta.confidence` | v3 launch |
