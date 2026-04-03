# Accuracy Method

## Ground truth sources
1. Nepal Government holiday publications (MoHA).
2. Rashtriya Panchang overlaps for festival/tithi checks.

## Measurement model
1. Single-day festivals: match if main day matches official date.
2. Multi-day festivals: match if start day matches official start.
3. Panchanga checks: compare tithi identity and boundary behavior.

## Core gates
1. BS conversion overlap fixtures must be exact in official range.
2. Udaya tithi boundary corpus must pass.
3. Adhik Maas historical corpus must pass.
4. Sankranti crossing tests must pass.

## Reporting artifacts
- `reports/authority_dashboard.json` (generated artifact)
- `reports/conformance_report.json` (generated artifact)
- `reports/evaluation_v4/evaluation_v4.json` (track-aware evaluation artifact)
- `data/ground_truth/*`

## Reproducibility contract

- Runtime benchmark summary: `GET /api/reliability/benchmark-manifest`
- Public truth/dispute surface: `GET /api/festivals/disputes`
- Proof capsule: `GET /api/festivals/{festival_id}/proof-capsule`
- The public benchmark story should always preserve:
  - evaluation track
  - conflict policy
  - abstention policy
  - report hash
  - engine manifest hash
  - source snapshot hashes

## Confidence policy
- `official`: lookup-backed official range
- `computed`: algorithmic ephemeris output
- `estimated`: projected output outside official table confidence zone

## Supported range contract

- Exact-supported BS years: `2070-2095`
- High-confidence computed range: the current ephemeris-supported product range
  where outputs are deterministic but not backed by the official lookup table
- Estimated range: sankranti-based projection outside the exact-supported table
- Unsupported range: any request beyond the enforced estimated bounds
