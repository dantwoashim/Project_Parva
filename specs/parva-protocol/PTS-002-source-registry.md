# PTS-002 Source Registry

## Data model

Source records identify public evidence used by a release.

## Required fields

- `source_id`
- `source_name`
- `source_tier`

## Source tiers

Allowed tiers are `official`, `semi_official`, `public_corpus`, `publisher`, `calculated`, `fixture`, `research`, `private`, and `unknown`.

## Boundary

Fixture, research, private, calculated, and weak source rows must not be represented as official authority.
