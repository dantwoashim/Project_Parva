# Source Registry

The source registry records public-safe metadata about the source material associated with a release.

The first registry is:

```text
data/public/releases/parva-bs-public-demo.sources.json
```

## Why The Registry Exists

Not every calendar source has the same claim strength. A source registry keeps source identity, source tier, claim support level, and review notes explicit instead of hiding them inside code or data tables.

## Source Fields

Each source entry includes:

- `source_id`
- `source_name`
- `source_tier`
- `description`
- `claim_support_level`
- `url`, when public and useful
- `reviewed_at`, when reviewed for the release
- `notes`

## Source Tiers

The public registry schema supports:

- `official_verified`
- `printed_verified`
- `public_witness`
- `publisher_reference`
- `software_table_reference`
- `third_party_reference`
- `needs_review`

Weak or convenience references must not be treated as official proof.

## Public Safety Boundary

The public registry contains metadata, not private source dumps. It does not include private future month values, corrected future values, private model outputs, or client-specific material.

Future-BS research output remains:

```text
computed_prediction_not_official
```

Official publication overrides computed output.
