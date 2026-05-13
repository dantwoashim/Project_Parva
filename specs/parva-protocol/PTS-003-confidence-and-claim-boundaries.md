# PTS-003 Confidence and Claim Boundaries

## Confidence labels

Allowed labels are `official_verified`, `source_backed`, `calculated`, `fixture_only`, `research_preview`, `disputed`, `unsupported`, and `unknown`.

## Claim boundary

Every public temporal result must include a claim boundary. The default public boundary is not legal, tax, payroll, banking, or regulatory authority.

## Conformance

An implementation fails source-aware conformance if fixture or research data supports an official-grade claim.
