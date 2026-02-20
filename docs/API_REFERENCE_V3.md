# API Reference (v3 Public)

Base URL (local): `http://localhost:8000/v3/api`

## Core Calendar
- `GET /calendar/today`
- `GET /calendar/convert?date=YYYY-MM-DD`
- `GET /calendar/convert/compare?date=YYYY-MM-DD`
- `GET /calendar/tithi?date=YYYY-MM-DD&latitude=&longitude=`
- `GET /calendar/panchanga?date=YYYY-MM-DD`
- `GET /calendar/panchanga/range?start=YYYY-MM-DD&days=7`

## Festivals
- `GET /festivals?quality_band=computed|provisional|inventory|all&algorithmic_only=true|false`
- `GET /festivals/upcoming?days=90&quality_band=computed|provisional|inventory|all`
- `GET /festivals/{id}?year=2026`
- `GET /festivals/{id}/explain?year=2026`
- `GET /festivals/{id}/dates?years=3`
- `GET /festivals/on-date/YYYY-MM-DD`
- `GET /festivals/coverage`
- `GET /festivals/coverage/scoreboard`

## Personal Stack
- `GET /personal/panchanga?date=YYYY-MM-DD&lat=&lon=&tz=`
- `GET /muhurta?date=YYYY-MM-DD&lat=&lon=&tz=&birth_nakshatra=`
- `GET /muhurta/auspicious?date=YYYY-MM-DD&type=general|vivah|griha_pravesh|travel|upanayana&lat=&lon=&tz=&birth_nakshatra=&assumption_set=np-mainstream-v2|diaspora-practical-v2`
- `GET /muhurta/rahu-kalam?date=YYYY-MM-DD&lat=&lon=&tz=`
- `GET /kundali?datetime=ISO8601&lat=&lon=&tz=`
- `GET /kundali/lagna?datetime=ISO8601&lat=&lon=&tz=`


## Engine Quality
- `GET /engine/calendars`
- `GET /engine/convert?date=YYYY-MM-DD&calendar=bs|ns|tibetan|islamic|hebrew|chinese|julian`
- `GET /engine/plugins/quality`
  - includes `stage1` + `stage2` validation cohorts
  - includes per-plugin `confidence_calibration` and error-budget checks

## Feeds
- `GET /feeds/all.ics?years=2&lang=en`
- `GET /feeds/national.ics?years=2&lang=en`
- `GET /feeds/newari.ics?years=2&lang=en`
- `GET /feeds/custom.ics?festivals=dashain,tihar&years=2&lang=en`

## Reliability + Provenance (public read)
- `GET /reliability/status`
- `GET /provenance/root`
- `GET /explain/{trace_id}`

## Response Metadata
Personal-stack endpoints include:
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
Set `PARVA_ENABLE_EXPERIMENTAL_API=true` to enable them.
