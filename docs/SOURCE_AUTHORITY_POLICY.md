---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Source Authority Policy

Status: canonical source-tier policy.

This policy defines the source authority tiers used by trust artifacts, protocol source records, public source registries, webhook schemas, public source-tier docs, and runtime source metadata.

The canonical runtime list lives in `backend/app/core/source_authority.py`.

## Canonical Tiers

| Tier | Who can use it | Public output? | Official-looking claims? | Human review? | Public offline bundle? | Conflict rule |
|---|---|---:|---:|---:|---:|---|
| `official` | Reviewed source records tied to an official publication such as MoHA, NPNS, NRB, or another legal authority | Yes | Only as source interpretation, never as Parva authority | Yes | Yes | Overrides weaker tiers when the publication is in scope |
| `semi_official` | Authority-adjacent sources, notices, institutional pages, or delegated publications | Yes | No | Yes | Yes | Loses to `official`; beats printed, public witness, software, and third-party rows |
| `printed_verified` | Human-reviewed printed calendars or panchanga publications | Yes | No | Yes | Yes | Loses to official or semi-official sources; beats weaker references |
| `public_witness` | Public dated material linking AD and BS facts | Yes | No | Yes | Yes | Supports triangulation; does not override higher authority |
| `publisher_reference` | Publisher, project, or documentation references | Yes | No | Usually no | Yes | Used for contracts and docs, not source authority |
| `software_table_reference` | Static tables or open-source software references | Yes | No | No | Yes | Comparison and reproducibility only |
| `third_party` | App, website, or third-party comparison source | Yes, with warnings | No | Yes for high-stakes use | Yes, if redistribution-safe metadata only | Never official by itself |
| `calculated` | Declared algorithms, astronomical engines, or deterministic computation | Yes | No | Review required for high-stakes use | Yes | Does not override published authority |
| `fixture` | Test, demo, or shape-only source data | No for public claims | No | No | No, except clearly labeled conformance-only material | Cannot resolve real source conflicts |
| `research_private` | Private source archives, model artifacts, future-BS research, or sensitive analysis | No | No | Yes | No | Private research only; public routes may expose boundary metadata |
| `unknown` | Unclassified or incomplete source metadata | No | No | Yes | No | Must be reviewed or downgraded to unsupported |

## Required Labels

Public responses must avoid ambiguous labels such as `official_verified` as a source tier. `official_verified` remains a confidence label in older API metadata, not a source authority tier.

Legacy aliases normalize as follows:

| Legacy label | Canonical source tier |
|---|---|
| `official_verified` | `official` |
| `public_corpus` | `software_table_reference` |
| `publisher` | `publisher_reference` |
| `third_party_reference` | `third_party` |
| `public_daily_witness` | `public_witness` |
| `research` or `private` | `research_private` |

## Official-Source Boundaries

An official source can support source-aware interpretation, but Parva must still say:

- the source remains the authority
- Parva is not official authority
- extraction and digitization require human review
- official publication overrides computed output
- legal, tax, payroll, banking-contract, and regulatory decisions require the relevant authority or institution

## Tests

The canonical tier contract is enforced by:

```bash
python -m pytest tests/trust/test_source_authority_tiers.py -q
python tools/validate_schemas.py
```

