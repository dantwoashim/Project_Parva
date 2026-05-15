# Broad Exception Audit

Generated artifact from the focused execution sprint.

Status after the follow-up execution pass: green.

Command to refresh:

```bash
python -m ruff check backend scripts packages --select BLE001
```

Priority review areas:

- billing mutation and payment paths,
- trust/provenance mutation,
- calendar conversion,
- Future-BS route gating,
- RuleLang execution,
- API middleware.

Current evidence:

```text
python -m ruff check backend scripts packages --select BLE001
All checks passed!
```

The fix narrowed broad catches in calendar ephemeris, lunar, muhurta, Nepal
Sambat, Future-BS research helpers, route plugins, backend tools, and release
scripts. Catch-all behavior should not be reintroduced without a clear process
boundary and a structured error path.
