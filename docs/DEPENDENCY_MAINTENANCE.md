---
status: active
tier: 1
lane: operations
owner: platform-team
---

# Dependency Maintenance

Project Parva dependency upgrades are handled as a scheduled release-hardening
lane, not mixed into feature or remediation branches.

## Cadence

- Run the dependency refresh checklist at least monthly.
- Run it immediately for any security advisory that affects a direct or
  transitive dependency in Python, the frontend, the JavaScript SDK, or the
  local verifier kernel.
- Keep major-version upgrades in separate changes from patch/minor refreshes.

## Order

1. Python constraints and optional dev/test dependencies.
2. Frontend dependencies and lockfile.
3. `packages/parva-js` dependencies and lockfile.
4. `packages/parva-local-kernel` dependencies and lockfile.

## Required Checks

```powershell
py -3.11 -m pip_audit --strict --requirement requirements\constraints.txt
cd frontend
npm audit --audit-level=low
npm outdated
npm run lint
npm test -- --run
npm run build
cd ..\packages\parva-js
npm audit --audit-level=low
npm outdated
npm test
cd ..\parva-local-kernel
npm audit --audit-level=low
npm outdated
npm test
cd ..\..
py -3.11 scripts\release\verify_public.py
```

## Policy

- Do not upgrade dependencies until the current repository state is already
  passing the focused and public release checks.
- Apply one ecosystem at a time so regressions have a narrow cause.
- Record CVE identifiers or advisory URLs in the change summary when a security
  update is the reason for the refresh.
- Leave known-good major versions pinned until the full release gate proves the
  migration safe.

