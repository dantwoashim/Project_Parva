---
status: stable
tier: 1
lane: operations
last_verified: 2026-05-14
owner: platform-team
---

# RuleLang Security

RuleLang is intentionally not a general programming language.

Rules are structured JSON and can call only the allowlisted temporal functions documented in `docs/RULELANG_BUILTINS.md`.

## Forbidden

RuleLang does not allow:

- arbitrary code execution
- Python `eval`
- Python `exec`
- shell commands
- arbitrary imports
- filesystem reads or writes
- network calls
- environment variable access
- dynamic function names outside the allowlist
- unbounded loops
- private rule loading in public mode

## Execution Bounds

Current public safety bounds:

| Limit | Value |
|---|---|
| Max steps | 128 |
| Default loop iterations | 32 |
| Absolute loop iterations | 366 |
| Max trace steps | 256 |
| Max condition depth | 16 |
| Max input payload | 8192 bytes |

If a rule exceeds its loop bound, execution fails with `MAX_ITERATIONS_EXCEEDED`.

## Public and Private Boundary

Public mode loads only `data/rules/public/`.

Private rule loading requires explicit private configuration and is not part of the public demo.

Public traces must not include secrets, local absolute paths, private archives, or raw private source content.

## Claim Boundary

RuleLang outputs are institutional decision support. They are not legal, tax, regulatory, payroll, or banking-contract final authority.
