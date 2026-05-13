# Evidence Packets

Evidence packets explain how Project Parva produced a temporal answer.

They are useful for audits, debugging, reproducibility, and release pinning. They are not legal certificates and do not claim official government authority.

## Supported Public Packet Types

- `date_conversion`
- `compliance_decision`
- `rule_execution`

Layer 5 uses the existing calendar conversion and compliance services. Layer 7 adds RuleLang execution packets for structured institutional rules. Evidence packet generation does not duplicate conversion or rule logic.

## Packet Shape

Each packet includes:

- packet id
- packet type
- generated timestamp
- input
- result
- release id
- source records
- confidence
- claim boundary
- warnings
- trace id
- packet hash
- signature status

Rule execution packets also include rule id, rule version, decision status, reason codes, trace summary, and TimeGraph fact ids where available.

The public signature status is:

```text
unsigned_public_preview
```

This means the packet has a stable SHA-256 hash but is not production-grade cryptographic signing.

## CLI Example

```bash
python scripts/parva_evidence_packet.py --type date_conversion --ad-date 2026-04-14
```

Compliance decision example:

```bash
python scripts/parva_evidence_packet.py --type compliance_decision --bs-date 2082-04-02 --profile-id nepal_private_company_default
```

## Public Safety

Public evidence packets must not include private archives, private future-BS vectors, corrected future values, local absolute paths, secrets, or client-specific content.
