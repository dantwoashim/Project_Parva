# PTS-002 Source Registry

## Data model

Source records identify public evidence used by a release.

## Required fields

- `source_id`
- `source_name`
- `source_tier`

## Source tiers

Allowed tiers are `official`, `semi_official`, `printed_verified`, `public_witness`, `publisher_reference`, `software_table_reference`, `third_party`, `calculated`, `fixture`, `research_private`, and `unknown`.

## Boundary

Fixture, research, private, calculated, and weak source rows must not be represented as official authority.
