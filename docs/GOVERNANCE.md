# Governance Model (Week 39-40, Plan Week 85-88)

## Goals
- Make rule changes auditable.
- Prevent silent date logic drift.
- Keep cultural/official source evidence attached to each decision.

## RFC Workflow
1. Contributor opens a **Rule Change RFC** with impact, sources, and test plan.
2. Maintainers review technical validity and source quality.
3. At least one reviewer provides `Reviewed-by:` sign-off.
4. Contributor includes `Signed-off-by:` in PR text.
5. Merge only after automated tests and governance checks pass.

## Required Metadata for Rule PRs
- Rule IDs touched
- Year/date examples before vs after
- Source list (primary references)
- Risk assessment (boundary cases, regional variations)
- Rollback note

## Reviewer Roles
- **Domain reviewer**: validates cultural and source correctness.
- **Engine reviewer**: validates algorithmic and API impact.

## Verification Script
Use:
- `python3 scripts/governance/verify_approval.py <file.md>`

Script ensures required sign-off/evidence sections exist.

## Signed Trail
Each accepted rule change should include these markers in PR/RFC text:
- `Reviewed-by: <name>`
- `Signed-off-by: <name>`
- `## Evidence`
- `## Sources`
