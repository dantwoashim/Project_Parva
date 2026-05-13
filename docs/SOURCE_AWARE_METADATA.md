# Source-Aware Metadata

Project Parva treats temporal output as a claim. Public responses should preserve source, confidence, version, warning, and claim-boundary metadata where the response makes a calendar, fiscal, festival, or panchanga claim.

## Metadata Shape

Core public responses may include:

```json
{
  "meta": {
    "source": {
      "id": "parva_public_bs_ad_corpus",
      "label": "Parva public BS/AD corpus",
      "tier": "public_corpus",
      "authority": "derived_reference_not_legal_authority",
      "version": "parva-public-calendar-v1"
    },
    "confidence": "source_backed",
    "data_version": "parva-public-calendar-v1",
    "release_id": "parva-bs-public-demo",
    "claim_boundary": "public_corpus_reference_only",
    "warnings": ["not_legal_tax_or_banking_contract_authority"],
    "trace_id": "request-trace-id",
    "result_class": "ad_to_bs_conversion"
  }
}
```

Existing top-level fields remain available for compatibility. Integrations should store the `meta` object alongside the result.

## Source Tiers

| Tier | Meaning |
|---|---|
| `official` | Structured official-source evidence is available for the specific public window |
| `public_corpus` | Public deterministic corpus or table evidence, not legal authority |
| `publisher` | Publisher or public documentation reference |
| `calculated` | Deterministic computation from declared engine logic |
| `fixture` | Test or demo data only |
| `research` | Research-preview or future-risk metadata |
| `private` | Private deployment source, not required for public tests |
| `unknown` | Fallback only, should be rare |

## Confidence Levels

| Confidence | Meaning |
|---|---|
| `official_verified` | Backed by structured official-source evidence in the public or private source policy |
| `source_backed` | Backed by public corpus or known source, but not official authority |
| `calculated` | Deterministic computed output from a declared algorithm or engine |
| `fixture_only` | Test/demo data only, never authoritative |
| `research_preview` | Experimental future-risk or model metadata |
| `disputed` | Sources conflict and no single source can be treated as uncontested |
| `unsupported` | Outside declared range or no usable support |
| `unknown` | Metadata fallback when source classification is unavailable |

Fixture, research, static lookup, or estimated data must never be labeled `official_verified`.

## Claim Boundaries

Public claim-boundary values include:

- `calendar_computation_not_legal_authority`
- `official_source_interpretation_not_legal_advice`
- `public_corpus_reference_only`
- `astronomical_calculation_subject_to_source_model`
- `enterprise_decision_support_not_legal_authority`
- `research_preview_not_safe_for_legal_or_payroll_use`
- `fixture_data_not_authoritative`

These values are intentionally precise. Parva is not an official government calendar publication, legal authority, tax authority, banking-contract authority, or payroll authority.

## Unsupported Ranges

Unsupported or out-of-range requests should fail with a 4xx error instead of returning fake certainty. Error responses include a traceable error envelope:

```json
{
  "detail": "Invalid date format. Use YYYY-MM-DD",
  "request_id": "trace-id",
  "version": "3.0.0",
  "error": {
    "code": "BAD_REQUEST",
    "message": "Invalid date format. Use YYYY-MM-DD",
    "details": {},
    "trace_id": "trace-id"
  }
}
```

## Public, Private, Fixture, And Research Data

- Public corpus data can support reproducible public API responses.
- Private source archives are optional and are not required for public verification.
- Fixture data is only for shape, demo, or test behavior.
- Future-BS public output is limited to research capability metadata and remains `computed_prediction_not_official`.
- Enterprise compliance output is decision support for working-day, fiscal-period, and review-required status. It is not legal, tax, payroll, banking-contract, or government authority.

Official publication and institution-specific policy override computed output.
