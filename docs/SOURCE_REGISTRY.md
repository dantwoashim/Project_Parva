# Source Registry

The source registry records public-safe metadata about the source material associated with a release.

The first registry is:

```text
data/public/releases/parva-bs-public-demo.sources.json
```

The public API response metadata uses matching source IDs where practical, including:

- `parva_structured_official_bs_window`
- `parva_public_bs_ad_corpus`
- `parva_static_lookup_table`
- `parva_astronomical_engine`
- `parva_public_festival_rules`
- `parva_enterprise_compliance_profiles`
- `parva_future_bs_risk_research`

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

- `official`
- `semi_official`
- `public_corpus`
- `publisher`
- `calculated`
- `fixture`
- `research`
- `private`
- `unknown`

Weak or convenience references must not be treated as official proof.

## API Metadata Relationship

Public API responses may include:

```json
{
  "meta": {
    "source": {
      "id": "parva_static_lookup_table",
      "tier": "public_corpus",
      "authority": "derived_reference_not_legal_authority"
    },
    "confidence": "source_backed",
    "claim_boundary": "public_corpus_reference_only"
  }
}
```

The registry identifies the source family. The response metadata tells clients how strong the current result claim is.

## Public Safety Boundary

The public registry contains metadata, not private source dumps. It does not include private future month values, corrected future values, private model outputs, or client-specific material.

Future-BS research output remains:

```text
computed_prediction_not_official
```

Official publication overrides computed output.
