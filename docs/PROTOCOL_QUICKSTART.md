---
status: draft
tier: 2
lane: protocol
last_verified: 2026-05-14
owner: protocol-team
---

# Protocol Quickstart

Inspect protocol version:

```bash
curl https://api.prabinghimire1.com.np/v3/api/protocol/version
```

Run local conformance:

```bash
python scripts/parva_conformance.py --target local --level parva_core
```

Issue a hash-only preview credential:

```bash
python scripts/parva_credential_issue.py --type date_conversion --bs-date 2083-01-01
```
