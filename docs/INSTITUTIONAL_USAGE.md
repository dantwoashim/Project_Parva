# Institutional Usage Guide

This document helps universities/government teams adopt Parva responsibly.

## Recommended Practices
- Consume versioned endpoints (`/v2/api/...`) only.
- Store returned provenance + confidence metadata alongside dates.
- Re-run internal verification using benchmark packs before publishing official notices.

## Minimum Integration Checklist
- Use `/v2/api/calendar/convert` and `/v2/api/calendar/panchanga`.
- Check `confidence` and `uncertainty` on each date.
- Archive response `provenance` payload for audit trails.
- Respect `policy` metadata and attach disclaimer for public-facing outputs.

## Operational Workflow
1. Pull precomputed artifacts for target years.
2. Validate critical observances against your official workflow.
3. Publish with source and confidence annotations.
