# Year 1 Week 1 — Ritual Timeline Adapter Specification

## Problem
Frontend `RitualTimeline` expects:

```json
{
  "preparation": "optional string",
  "days": [
    {
      "name": "string",
      "significance": "string",
      "events": [
        {
          "time": "string",
          "title": "string",
          "description": "string",
          "location": "string",
          "participants": "string",
          "offerings": ["string"]
        }
      ]
    }
  ]
}
```

Current data sources are heterogeneous:
1. `daily_rituals` (array of day objects with nested `rituals`)
2. `simple_rituals` (legacy list/string/object formats)
3. `ritual_sequence` (already close to frontend schema in some entries)

Without normalization, Ritual tab can render empty or malformed events.

## Source Shape Inventory

### A) `daily_rituals` (current `festivals.json` pattern)
- Top-level: array of day objects.
- Day object: `day`, `name`, `name_nepali`, `description`, `rituals[]`, `is_main_day`.
- Ritual object: `order`, `name`, `description`, `time_of_day`, `location`.

### B) `simple_rituals` (legacy)
- Could be:
  - array of strings
  - array of objects
  - object containing `days`.

### C) `ritual_sequence` (legacy/alternate)
- Usually closest to target shape; should pass through with minimal mapping.

## Adapter Contract

### Function
`normalize_ritual_data(festival: dict) -> dict | None`

### Output Guarantee
If any ritual data exists, output **must** contain:
1. `days` as non-empty array
2. each day with `events` as array of objects
3. each event with at least `title` (string)

If no ritual data exists, return `None`.

## Transformation Rules

### Rule 1 — `ritual_sequence` passthrough
If `festival.ritual_sequence.days` exists:
- map each event with defaults:
  - `title`: required; fallback to `"Ritual"`
  - `time`: fallback `"—"`
- preserve `preparation` if present.

### Rule 2 — `daily_rituals` to timeline
For each day in `daily_rituals`:
1. `name` = `day.name` or `Day {day.day}`
2. `significance` = `day.description`
3. `events` = map `day.rituals` sorted by `order`:
   - `title` = `ritual.name`
   - `description` = `ritual.description`
   - `time` = `ritual.time_of_day` mapped:
     - `morning` -> `Morning`
     - `afternoon` -> `Afternoon`
     - `evening` -> `Evening`
     - `all day`/missing -> `—`
   - `location` = `ritual.location`
   - `participants` = optional
   - `offerings` = optional array

### Rule 3 — `simple_rituals` array of strings
Create one day:
- `name` = festival name
- `events` = each string -> `{ "title": string, "time": "—" }`

### Rule 4 — `simple_rituals` array of objects
Create one day:
- map objects using field aliases:
  - `title`: `title` || `name` || `ritual`
  - `description`: `description` || `details`
  - `time`: `time` || `time_of_day` || `—`

### Rule 5 — empty/malformed fallback
If after normalization no valid events exist:
- return `None`.

## Validation Rules
Post-transform validations:
1. `days.length >= 1`
2. each day has `events` array
3. each event contains non-empty `title`
4. strip null/undefined values from event payload

## Example Mapping

### Input (`daily_rituals`)
```json
{
  "name": "Dashain",
  "daily_rituals": [
    {
      "day": 1,
      "name": "Ghatasthapana",
      "description": "Festival begins",
      "rituals": [
        { "order": 1, "name": "Ghata Sthapana", "description": "Setup kalash", "time_of_day": "morning", "location": "Home puja room" }
      ]
    }
  ]
}
```

### Output
```json
{
  "days": [
    {
      "name": "Ghatasthapana",
      "significance": "Festival begins",
      "events": [
        {
          "time": "Morning",
          "title": "Ghata Sthapana",
          "description": "Setup kalash",
          "location": "Home puja room"
        }
      ]
    }
  ]
}
```

## Test Cases (Week 2 implementation target)
1. `daily_rituals` with nested rituals -> renders non-empty timeline.
2. `simple_rituals` string array -> converts to event titles.
3. `ritual_sequence.days` -> passthrough with defaults.
4. malformed entries -> returns `None`.
5. event ordering honors `order` in source.

## Integration Point
- Preferred: backend adapter (`backend/app/festivals/adapters.py`) so frontend receives one stable schema.
- Temporary fallback: keep frontend normalization for safety until backend adapter is fully live.
