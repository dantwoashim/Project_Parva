---
status: public-beta
audience: developer
---

# Developer Experience

The first developer path is:

1. Read [Quickstart](QUICKSTART.md).
2. Run `python scripts/verify_environment.py`.
3. Call stable BS/AD conversion.
4. Call fiscal or working-day logic.
5. Inspect source, confidence, maturity, and review-boundary metadata.
6. Run `python scripts/release/verify_public.py` before changing public claims.

Developer-facing promises are intentionally narrow:

- deterministic calendar infrastructure,
- public-safe source and trust metadata,
- clear route maturity boundaries,
- SDK defaults that avoid private research routes,
- reproducible verification commands.

Known friction still tracked:

- `frontend/src/redesign/ParvaExperience.jsx` remains large and is now measured
  by `scripts/frontend/check_component_size.py`.
- Public docs are being compressed around the stable route set instead of every
  research or preview subsystem.
- The default Windows shell may resolve Python 3.10 and Node 25; the verifier
  reports this clearly.

## Ten-Minute Adoption Target

The developer path should fit this sequence:

| Minute | Outcome |
| --- | --- |
| 0-2 | Read stable route and authority boundary in [Quickstart](QUICKSTART.md). |
| 2-4 | Install SDK or use REST examples. |
| 4-6 | Convert BS/AD, validate an invalid BS date, and inspect metadata. |
| 6-8 | Call fiscal-year and working-day support. |
| 8-10 | Run public verification or inspect the verification matrix generated artifact. |

If a route is preview, research-private, or unsupported, the docs should say so
before a developer has to discover it through a failed request.

## Non-Programmer Adoption

Spreadsheet users can start from [Parva Sheets](../packages/parva-sheets/README.md).
The Google Apps Script and Excel Office Script examples expose public v3 API
helpers for BS/AD conversion, holiday checks, fiscal years, and working-day
status. Metadata-aware formulas can return review-required and claim-boundary
columns where the spreadsheet format allows it.

These examples are not marketplace publications and do not grant official or
institutional authority. They are public-beta distribution examples for review,
internal testing, and vendor audit preparation.
