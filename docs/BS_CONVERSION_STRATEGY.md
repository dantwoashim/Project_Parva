# BS Conversion Strategy (Dual-Mode)

## Goal
Provide wide BS conversion coverage while being explicit about trust level.

## Modes
- `official`: Lookup-table conversion for BS `2070-2095` (authoritative committee tables).
- `estimated`: Sankranti-based astronomical estimation outside lookup range.

## Why Dual-Mode
The official BS calendar is committee-published and not purely formulaic. A purely astronomical model can be close, but it will not be identical for every day in overlap years. The API therefore exposes confidence, not hidden assumptions.

## Official Path
- Data source: `app.calendar.constants.BS_CALENDAR_DATA`
- Year boundaries and month lengths are read directly from official table rows.
- Conversion is deterministic and exact within table range.

## Estimated Path
- Compute Mesh Sankranti for the corresponding Gregorian year.
- Compute all 12 sankranti month starts for the BS year using ephemeris.
- Apply Nepal month-start convention:
  - transit before sunrise: month starts same local date
  - transit after sunrise: month starts next local date
- Month/day derived from intervals between adjacent month starts.

## Confidence Contract
Every endpoint returning BS dates includes:
- `confidence: "official" | "estimated"`

Rules:
- Gregorian in official overlap -> `official`
- Gregorian outside overlap -> `estimated`
- Manual overrides -> treated as `official`

## Verification Artifacts
- Overlap fixture: `tests/fixtures/bs_overlap_comparison.json`
- Report: `docs/BS_OVERLAP_REPORT.md`
- Comparison endpoint: `GET /api/calendar/convert/compare?date=YYYY-MM-DD`

## User-Facing Guidance
- Use `official` dates for legal/institutional outputs.
- Use `estimated` dates for historical/future exploratory ranges.
- For `estimated` dates near month boundaries, small shifts can occur versus future official publications.
