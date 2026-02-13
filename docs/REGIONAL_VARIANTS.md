# Regional Variants (Initial Engine)

This module introduces a first-pass variant engine for festivals with known regional/tradition interpretation differences.

## Data Source
- `data/variants/regional_map.json`

## API
- `GET /v2/api/festivals/{festival_id}/variants?year=YYYY`

## Variant Fields
- `profile_id`
- `tradition`
- `region`
- `date`
- `confidence`
- `rule_used`
- `notes`

## Current Scope
- Initial profile set for demonstration and UI/API integration:
  - Nepali mainstream
  - Newar Kathmandu Valley
  - Diaspora North Indian profile

## Notes
- Variants are additive metadata over primary calculation output.
- Default endpoints still return primary interpretation unless variant endpoint is requested.
