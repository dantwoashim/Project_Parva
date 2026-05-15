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
