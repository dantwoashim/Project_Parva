# API Error Handling

## Common Status Codes
- `200` Success
- `400` Invalid input (date format, invalid BS date)
- `404` Festival/resource not found
- `422` Validation error (query/body constraints)
- `500` Calculation/runtime error

## Typical Error Payload
```json
{
  "detail": "Invalid date format. Use YYYY-MM-DD"
}
```

## Retry Guidance
- Retryable:
  - Temporary network failures
  - `500` from transient engine/source issues
- Non-retryable:
  - `400` / `422` malformed input
  - `404` unknown resource ID

## Input Validation Tips
- Gregorian dates must be `YYYY-MM-DD`
- BS month must be `1-12`
- Latitude range `-90..90`, longitude `-180..180`

## Confidence-Specific Handling
- If `bikram_sambat.confidence == "official"`:
  - treat as authoritative lookup-backed output
- If `bikram_sambat.confidence == "estimated"`:
  - display estimate indicator in UI
  - use `estimated_error_days` for user messaging

## Deprecation Headers (Legacy `/api/*`)
Legacy unversioned endpoints include:
- `Deprecation: true`
- `Sunset: <HTTP date>`
- `Link: <...>; rel="successor-version"`

Use `/v2/api/*` for forward-compatible integrations.
