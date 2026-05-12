# Temporal SBOM

A temporal SBOM records the calendar releases and temporal data contracts that a downstream system depends on.

Most software bills of materials focus on code packages. Nepali calendar systems also depend on calendar releases, source policy, fiscal-year assumptions, and reconciliation workflows. Those dependencies should be visible.

## Why It Matters

Temporal dependencies affect:

- fiscal periods
- schedules
- date validation
- calendar conversion
- audit trails
- review workflows

If a calendar release changes, operators need to know which systems used the old release and which records may require review.

## Schema

The public alpha schema is:

```text
schemas/temporal-sbom.schema.json
```

Example shape:

```json
{
  "system": "loan-schedule-service",
  "generated_at": "2026-05-12T00:00:00Z",
  "temporal_dependencies": [
    {
      "name": "parva-bs-calendar",
      "release": "parva-bs-public-demo",
      "hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
      "source_policy": "official_strict"
    }
  ]
}
```

The example is structural. It is not a private deployment manifest and does not include future month values.

## Operational Use

Teams can attach a temporal SBOM to release notes, service deployments, audit exports, or internal change approvals. When a calendar release is verified or updated, the SBOM identifies which systems need review.
