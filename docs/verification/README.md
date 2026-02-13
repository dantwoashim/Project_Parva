# Verification Artifacts

This directory tracks public verification outputs for Parva.

Contents should include:
1. Accuracy dashboard snapshots.
2. Differential comparison summaries (Parva vs MoHA/Rashtriya Panchang).
3. Discrepancy taxonomy and root-cause notes.
4. Quarterly verification reports.

Primary machine artifact is generated at:
- `reports/conformance_report.json`

Authority-track endpoints:
- `/v5/api/spec/conformance`
- `/v5/api/provenance/verify/trace/{trace_id}`
