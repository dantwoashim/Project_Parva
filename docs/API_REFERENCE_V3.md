# API Reference (v3 Public)

Base URL (deployment example): `https://your-host.example/v3/api`

Privacy-sensitive compute routes now support `POST` JSON bodies and should use
that shape by default. Legacy `GET` query forms remain available for
compatibility.

Practical integration guides:

- `docs/API_QUICKSTART.md`
- `docs/EMBED_GUIDE.md`

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
- `GET /festivals/{id}?year=2026`
- `GET /festivals/{id}/explain?year=2026`
- `GET /festivals/{id}/dates?years=3`
- `GET /festivals/on-date/YYYY-MM-DD`
- `GET /festivals/coverage`
- `GET /festivals/coverage/scoreboard`

### Festival detail ritual contract
`GET /festivals/{id}` includes canonical ritual shape:
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

## Personal Stack
- `POST /personal/panchanga` with JSON body `{ "date", "lat", "lon", "tz" }`
  - includes `local_sunrise`, `local_sunset`, `timezone_source`, `method_profile`, `assumption_set_id`, `quality_band`.
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
- `GET /engine/convert?date=YYYY-MM-DD&calendar=bs|ns|tibetan|islamic|hebrew|chinese|julian`
- `GET /engine/plugins/quality`

## Reliability + Provenance (public read)
- `GET /reliability/status`
- `GET /provenance/root`
- `GET /explain/{trace_id}`

## Metadata Expectations
Critical routes carry authority metadata fields needed by Authority Mode:
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

## Experimental API Tracks
`/v2`, `/v4`, `/v5` are disabled by default.
Set `PARVA_ENABLE_EXPERIMENTAL_API=true` to enable non-public tracks for development.
