# Vendor Date Risk Audit

Status: audit checklist for external products that handle Nepali dates.

This checklist helps compare vendor behavior against Parva Protocol draft
expectations. It is not a certification program.

## Audit Areas

- Date conversion range and failure behavior
- Source citations and source-tier labels
- Future-date uncertainty labels
- Fiscal-year and compliance decision handling
- Holiday and observance source boundaries
- Evidence packet or trace availability
- Release manifest and artifact hash availability
- Offline verification support
- Human-review gates for payroll, banking, legal, and official-source claims
- Public claims and marketing language

## Required Evidence

Vendors should provide runnable examples, source citations, release version
metadata, documented error behavior, and a current compatibility report if they
claim compatibility with a Parva draft level.

## Red Flags

- Claims of official approval without an official source.
- Future calendar dates presented as final when the data is computed prediction.
- Silent fallback to low-confidence data.
- Private source use without a public/private data boundary.
- No reproducible release artifact or checksum trail.
