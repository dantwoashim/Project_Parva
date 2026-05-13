# TimeGraph Conflicts

TimeGraph treats conflicts as explicit graph objects. A conflict records that
two or more facts, sources, or derivations disagree or require review.

## Conflict Shape

```json
{
  "conflict_id": "conflict_fixture_public_timegraph",
  "conflict_type": "fixture_source_disagreement",
  "status": "fixture_only",
  "facts": [
    "fact_fixture_conflict_candidate_a",
    "fact_fixture_conflict_candidate_b"
  ],
  "sources": [
    "parva_public_bs_ad_corpus"
  ],
  "release_ids": [
    "parva-bs-public-demo"
  ],
  "summary": "Fixture-only conflict used to validate public conflict handling.",
  "resolution_policy": "fixture_only_no_real_claim",
  "requires_human_review": true,
  "confidence": "fixture_only",
  "warnings": [
    "fixture_conflict_not_real_source_disagreement"
  ]
}
```

## Real Versus Fixture Conflicts

If a public conflict is real, it must cite the involved facts, sources, release
ids, confidence, warning, and resolution policy.

If a conflict is only for testing the graph model, it must be labeled:

```text
fixture_only
```

Fixture conflicts must not be used as evidence that public sources disagree.

## Review Workflow

A conflict can point to:

- candidate facts
- supporting and contradicting sources
- release ids
- reason for review
- resolution policy
- confidence status
- warnings

The public API does not resolve conflicts silently. It exposes the review state
and claim boundary so downstream systems can decide how to handle uncertainty.

## Safety Boundary

Conflicts do not create official authority. Official publications and the
organization's own approved policy override TimeGraph review hints.
