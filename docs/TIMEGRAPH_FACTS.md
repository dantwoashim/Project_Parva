# TimeGraph Facts And Relationships

This document defines the public TimeGraph fact and relationship vocabulary.
The vocabulary is intentionally small so the public graph stays understandable
and reproducible from public artifacts.

## Temporal Fact Shape

Every fact includes:

```json
{
  "fact_id": "fact_bs_ad_2083_01_01",
  "fact_type": "bs_ad_mapping",
  "subject": {
    "calendar": "BS",
    "date": "2083-01-01"
  },
  "predicate": "maps_to",
  "object": {
    "calendar": "AD",
    "date": "2026-04-14"
  },
  "release_id": "parva-bs-public-demo",
  "source_ids": ["parva_public_bs_ad_corpus"],
  "confidence": "source_backed",
  "claim_boundary": "timegraph_query_not_legal_authority",
  "warnings": [],
  "metadata": {}
}
```

The example above uses a historical public demo date inside the public release
coverage.

## Supported Fact Types

| Fact type | Purpose |
|---|---|
| `bs_ad_mapping` | BS date maps to AD date |
| `ad_bs_mapping` | AD date maps to BS date |
| `month_length` | Public release month length for completed demo years |
| `weekday` | AD date weekday fact |
| `fiscal_period_membership` | Date belongs to a Nepali fiscal period |
| `profile_policy` | Compliance profile policy statement |
| `working_day_decision` | Profile-specific working-day decision sample |
| `source_claim` | Public source registry claim |
| `release_membership` | Artifact or source membership in a release |
| `conflict` | Conflict candidate used by a conflict record |

Additional fact types can be added only when existing Project Parva data
honestly supports them.

## Deterministic Fact ID Rules

Fact ids use stable slugs:

```text
fact_bs_ad_2083_01_01
fact_ad_bs_2026_04_14
fact_month_length_bs_2082_01
fact_weekday_ad_2026_04_14
fact_profile_policy_nepal_private_company_default
```

Random ids are avoided for deterministic facts.

## Relationship Shape

```json
{
  "relationship_id": "rel_fact_bs_ad_2083_01_01_supported_by_source_parva_public_bs_ad_corpus",
  "from_id": "fact_bs_ad_2083_01_01",
  "to_id": "source_parva_public_bs_ad_corpus",
  "type": "SUPPORTED_BY",
  "release_id": "parva-bs-public-demo",
  "confidence": "source_backed",
  "metadata": {}
}
```

## Supported Relationship Types

| Relationship | Meaning |
|---|---|
| `SUPPORTED_BY` | A source supports a fact |
| `CONTRADICTED_BY` | A source or fact contradicts another fact |
| `APPLIES_TO` | A profile, jurisdiction, or policy applies to a fact |
| `DERIVED_FROM` | A fact is derived from another fact |
| `COMPUTED_FROM` | A fact is computed from declared calendar logic |
| `BELONGS_TO` | A fact belongs to a period or grouping |
| `PINNED_TO_RELEASE` | A fact is bound to a release |
| `CONTAINS_FACT` | A release contains a fact |
| `REFERENCES_FACT` | An evidence packet or decision references a fact |
| `REQUIRES_REVIEW` | A fact or conflict should be reviewed |

## Claim Boundaries

The default TimeGraph claim boundary is:

```text
timegraph_query_not_legal_authority
```

Future-BS research outputs, where present in other surfaces, remain:

```text
computed_prediction_not_official
```

Weak or fixture data must not be promoted to official status.
