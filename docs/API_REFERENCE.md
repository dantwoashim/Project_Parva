# API Reference (v2)

Base URL: `http://localhost:8000/v2/api`

## Calendar

### `GET /calendar/today`
Returns Gregorian date, BS date (`official|estimated` confidence), tithi, method metadata, and `provenance`.

### `GET /calendar/convert?date=YYYY-MM-DD`
Converts Gregorian to BS with confidence fields.

### `GET /calendar/convert/compare?date=YYYY-MM-DD`
Returns `official` and `estimated` conversion side-by-side (overlap diagnostics).

### `GET /calendar/panchanga?date=YYYY-MM-DD`
Returns full panchanga values with astronomy method metadata and `provenance`.

## Festivals

### `GET /festivals`
List festivals (supports query filters like `category`, `search`).

### `GET /festivals/upcoming?days=30`
Upcoming festivals in date window.

### `GET /festivals/{id}?year=2026`
Festival detail + calculated date range for requested year.

### `GET /festivals/{id}/explain?year=2026`
Human-readable reasoning for calculated date (`calculation_trace_id` included).

### `GET /festivals/{id}/dates?years=3`
Projected date series for the next N years.

## Temples

### `GET /temples`
Temple list.

### `GET /temples/for-festival/{festival_id}`
Festival-linked temple set with role mapping.

### `GET /temples/{temple_id}`
Detailed temple info.

## Engine/Trust

### `GET /engine/config`
Active ephemeris and engine mode.

### `GET /engine/calendars`
List registered calendar plugins and their confidence characteristics.

### `GET /engine/convert?date=YYYY-MM-DD&calendar=bs|ns|tibetan|islamic|hebrew`
Convert Gregorian date with a selected calendar plugin.

### `GET /engine/observance-plugins`
List available observance plugins.

### `GET /engine/observances?plugin=...&rule_id=...&year=...&mode=...`
Compute one observance through selected plugin.
For Islamic plugin, `mode` supports `tabular`, `astronomical`, `announced`.

### `GET /provenance/root`
Current root + active snapshot hashes.

### `POST /provenance/snapshot/create`
Create new snapshot record (`snapshot_id`, dataset/rule hashes).

### `GET /provenance/snapshot/{snapshot_id}/verify`
Re-hash and verify snapshot integrity.

### `GET /provenance/proof?festival={id}&year={year}&snapshot={snapshot_id}`
Merkle inclusion proof for a festival date.

## Variants

### `GET /festivals/{id}/variants?year=YYYY`
Return documented regional/tradition observance variants.
