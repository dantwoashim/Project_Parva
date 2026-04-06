# Accuracy Method

This document describes how Parva validates calendar and festival outputs before they are published through the API and reference app.

## Source basis

Parva combines two source classes:

1. Official Nepal government calendar and holiday publications for supported overlap ranges.
2. Astronomical calculation through Swiss Ephemeris for dynamic calendar and festival computation.

## Validation rules

The validation pipeline checks four core areas:

1. BS/AD conversion fixtures in the official supported range.
2. Sunrise-based tithi boundary behavior.
3. Historical adhik-maas cases.
4. Sankranti crossing behavior.

## Generated validation artifacts

- `reports/conformance_report.json` (generated artifact)
- `reports/evaluation_v4/evaluation_v4.json` (generated artifact)
- `data/ground_truth/*`

## Runtime verification surfaces

- `GET /api/reliability/benchmark-manifest`
- `GET /api/reliability/boundary-suite`
- `GET /api/engine/manifest`

These endpoints expose the current engine identity, validation summary, and published boundary checks for the running deployment.

## Confidence bands

- `official`: backed by maintained overlap tables in the supported official range
- `computed`: calculated by the canonical ephemeris path with stable assumptions
- `estimated`: projection outside the strongest table-backed support zone

## Supported range

- Exact-supported BS years: `2070-2095`
- Computed range: deterministic ephemeris-backed output outside the official overlap table
- Estimated range: bounded projection outside the strongest supported conversion window
- Unsupported range: requests beyond enforced bounds
