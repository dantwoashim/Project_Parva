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
- `reports/authority_dashboard.json`
- `reports/conformance_report.json`
- `data/ground_truth/*`

## Confidence policy
- `official`: lookup-backed official range
- `computed`: algorithmic ephemeris output
- `estimated`: projected output outside official table confidence zone
