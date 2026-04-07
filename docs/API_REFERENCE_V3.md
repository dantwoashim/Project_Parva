# API Reference (v3 Public)

Base URL (deployment example): `https://your-host.example/v3/api`

Privacy-sensitive compute routes now support `POST` JSON bodies and should use
that shape by default. Legacy `GET` query forms remain available for
compatibility.

Practical integration guides:

- `docs/API_QUICKSTART.md`
- `docs/EMBED_GUIDE.md`

Selected routes also support an additive envelope mode.
Send header `X-Parva-Envelope: data-meta` to receive:

```json
{
  "data": { "...": "route payload" },
  "meta": {
    "confidence": "computed",
    "method": "ephemeris_udaya",
    "provenance": {},
    "uncertainty": {},
    "trace_id": "trace_...",
    "policy": {},
    "degraded": { "active": false, "reasons": [], "defaults_applied": [] }
  }
}
```

Without that header, the public v3 response shape remains unchanged.

## Temporal Cartography Endpoints
- `POST /temporal/compass` with JSON body `{ "date", "lat", "lon", "tz", "quality_band" }`
- `GET /festivals/timeline?from=YYYY-MM-DD&to=YYYY-MM-DD&quality_band=&category=&region=&lang=en|ne`
- `POST /muhurta/heatmap` with JSON body `{ "date", "lat", "lon", "tz", "type", "assumption_set" }`
- `POST /kundali/graph` with JSON body `{ "datetime", "lat", "lon", "tz" }`
- `GET /glossary?domain=panchanga|muhurta|kundali&lang=en|ne`

## Core Calendar
- `GET /calendar/today`
- `GET /calendar/convert?date=YYYY-MM-DD`
- `GET /calendar/convert/compare?date=YYYY-MM-DD`
- `GET /calendar/tithi?date=YYYY-MM-DD&latitude=&longitude=`
- `GET /calendar/panchanga?date=YYYY-MM-DD`
- `GET /calendar/panchanga/range?start=YYYY-MM-DD&days=7`
- `GET /resolve?date=YYYY-MM-DD&profile=&latitude=&longitude=&include_trace=true|false`

## Festivals
- `GET /festivals?quality_band=computed|provisional|inventory|all&algorithmic_only=true|false`
- `GET /festivals/upcoming?days=90&quality_band=computed|provisional|inventory|all`
- `GET /festivals/{festival_id}?year=2026`
- `GET /festivals/{festival_id}/explain?year=2026`
- `GET /festivals/{festival_id}/dates?years=3`
- `GET /festivals/on-date/{target_date}`
- `GET /festivals/coverage`
- `GET /festivals/coverage/scoreboard`

### Festival detail ritual contract
`GET /festivals/{festival_id}` includes canonical ritual shape:
```json
{
  "festival": {
    "ritual_sequence": {
      "days": [
        {
          "name": "Ghatasthapana",
          "events": [{ "title": "Kalash Sthapana" }]
        }
      ]
    }
  }
}
```

Festival detail also includes additive `completeness` signals so clients can show
truthful section-level status for narrative depth, ritual sequence coverage,
date resolution, and related observances.

## Personal Stack
- `POST /personal/panchanga` with JSON body `{ "date", "lat", "lon", "tz" }`
  - includes `sunrise`, `local_sunrise`, `local_sunset`, `timezone_source`, `method_profile`, `assumption_set_id`, `quality_band`.
  - sunrise fields use the canonical time-reference object shape:
  ```json
  {
    "local": "2026-02-15T06:44:00+05:45",
    "utc": "2026-02-15T00:59:00Z",
    "local_time": "06:44 AM"
  }
  ```
- `POST /muhurta` with JSON body `{ "date", "lat", "lon", "tz", "birth_nakshatra" }`
- `POST /muhurta/auspicious` with JSON body `{ "date", "type", "lat", "lon", "tz", "birth_nakshatra", "assumption_set" }`
  - includes `reason_codes[]`, `rank_explanation`, `confidence_score`.
- `POST /muhurta/rahu-kalam` with JSON body `{ "date", "lat", "lon", "tz" }`
- `POST /kundali` with JSON body `{ "datetime", "lat", "lon", "tz" }`
  - includes `insight_blocks[]` for plain-language sidebar mapping.
- `POST /kundali/lagna` with JSON body `{ "datetime", "lat", "lon", "tz" }`

## Feeds
- `GET /feeds/all.ics?years=2&lang=en`
- `GET /feeds/national.ics?years=2&lang=en`
- `GET /feeds/newari.ics?years=2&lang=en`
- `GET /feeds/custom.ics?festivals=dashain,tihar&years=2&lang=en`

## Engine Quality
- `GET /engine/calendars`
- `GET /engine/config`
- `GET /engine/manifest`
- `GET /engine/convert?date=YYYY-MM-DD&calendar=bs|ns|tibetan|islamic|hebrew|chinese|julian`
- `GET /engine/plugins/quality`

## Operational + Provenance Routes
- `GET /reliability/status`
- `GET /reliability/metrics`
- `GET /reliability/metrics.prom`
- `GET /reliability/boundary-suite`
- `GET /reliability/benchmark-manifest`
- `GET /reliability/differential-manifest`
- `GET /reliability/source-review-queue`
- `GET /provenance/root`
- `GET /provenance/proof`
- `GET /public/artifacts/manifest`
- `GET /explain/{trace_id}`

These read routes are part of the public v3 profile. Mutating provenance routes remain admin-only.

## Metadata Expectations
Integration-sensitive routes carry metadata fields that help clients render honest output:
- `engine_version`
- `calculation_trace_id`
- `confidence`
- `method`
- `method_profile`
- `quality_band`
- `assumption_set_id`
- `advisory_scope`
- `policy`
- `provenance`

`provenance` includes explicit attestation metadata. When no signing key is configured, Parva returns `attestation.mode = "unsigned"` instead of presenting a plain hash as a signature.

## Experimental API Tracks
`/v2`, `/v4`, `/v5` are disabled by default.
Set `PARVA_ENABLE_EXPERIMENTAL_API=true` to enable non-public tracks for development.
