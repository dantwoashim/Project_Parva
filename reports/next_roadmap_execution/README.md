# Next Roadmap Execution Report

Generated: 2026-05-15T19:58:47+05:45

## Verdict

The roadmap work moved Project Parva toward deterministic Nepali temporal infrastructure in the requested order: public verification first, developer adoption second, benchmark and accuracy foundations next, then optional AI-tool and MCP adapters, government packet, and vendor packet.

The public verification gate passed after the changes. This report does not claim official government approval, legal authority, tax authority, payroll authority, banking authority, official future BS dates, external certification, customer adoption, or production signing authority.

## What Changed

- Public verification is backed by narrowly allowlisted generated report artifacts.
- Developer docs now explain stable routes, SDK boundaries, errors, versioning, and unsupported Future-BS behavior.
- A public Nepali Time Reliability Benchmark v0 exists with 38 public-safe tasks and runnable baseline/Parva runners.
- The JPL/DE440 foundation is policy-bound: optional, private/research, hash-verified when present, and not required for public verification.
- External temporal rule profiles now separate astronomical computation from institutional decision authority.
- LangChain/LlamaIndex wrappers exist as safe public-route adapters with schema tests.
- MCP exists as an optional read-only adapter over the same stable public capabilities.
- Government and vendor packets are framed as proposal/conformance materials, not authority or adoption claims.

## Green Evidence

- `py -3.11 scripts/release/verify_public.py` passed the public reproducibility gate with 29 subchecks.
- Backend public pytest lane passed: 851 passed, 8 skipped.
- Frontend passed: lint, 120 tests, and production build.
- Python SDK tests passed: 16 tests.
- JavaScript SDK tests passed: 13 tests.
- AI-tool and MCP package tests passed: 11 tests.
- Benchmark runners executed: static baseline 20.53 percent, Parva 86.58 percent.
- JPL kernel hash verifier passed with configured present kernels verified and optional absent kernel skipped.

## Boundaries

Project Parva remains a source-backed reference implementation and verification layer. Official bodies decide holidays, Panchanga releases, civil calendars, and institutional rules. Parva helps encode, verify, distribute, test, and expose deterministic machine-readable behavior.
