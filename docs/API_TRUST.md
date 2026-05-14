---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Trust API

The Trust API exposes public-safe release and evidence metadata.

Base path:

```text
/v3/api/trust
```

## Endpoints

| Endpoint | Method | Purpose |
|---|---:|---|
| `/v3/api/trust/capabilities` | GET | Public trust surface metadata |
| `/v3/api/trust/sources` | GET | List source registry records |
| `/v3/api/trust/sources/{source_id}` | GET | Get one source record |
| `/v3/api/trust/releases` | GET | List public release manifests |
| `/v3/api/trust/releases/{release_id}` | GET | Get one release manifest |
| `/v3/api/trust/releases/{from_release}/diff/{to_release}` | GET | Diff two releases at metadata level |
| `/v3/api/trust/log` | GET | Read the public trust log |
| `/v3/api/trust/evidence/date-conversion` | POST | Create a date-conversion evidence packet |
| `/v3/api/trust/evidence/compliance-decision` | POST | Create a compliance decision evidence packet |

## Version Pinning

Supported trust routes accept:

```text
release_id=parva-bs-public-demo
x-parva-release-id: parva-bs-public-demo
```

Unknown release ids return 404.

## Date Conversion Evidence

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/trust/evidence/date-conversion \
  -H "Content-Type: application/json" \
  -d '{"ad_date":"2026-04-14"}'
```

The response includes the conversion result, source records, release id, confidence, claim boundary, warnings, trace id, and packet hash.

## Compliance Evidence

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/trust/evidence/compliance-decision \
  -H "Content-Type: application/json" \
  -d '{"profile_id":"nepal_private_company_default","bs_date":"2082-04-02"}'
```

Compliance packets preserve `requires_human_review` and reason codes from the compliance layer.

## Boundary

The Trust API is audit infrastructure. It is not a legal, tax, payroll, banking-contract, or regulatory final authority.

Public trust records support reproducibility and review. They do not promote weak, third-party, software-table, or research-preview evidence into official-grade claims.
