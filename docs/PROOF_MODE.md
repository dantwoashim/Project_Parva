# Proof Mode

Proof mode turns a Parva answer into a replay-verifiable artifact.

Supported values:

- `proof=none`
- `proof=compact`
- `proof=audit`
- `proof=replay`
- `proof=membrane`

## Example

```bash
curl "https://api.prabinghimire1.com.np/v3/api/calendar/convert?date=2025-04-14&proof=replay"
```

## What a Proof Contains

- canonical query
- explicit defaults
- identity hash
- result
- witness hash
- field provenance
- boundary vector
- source or method docket references
- policy trace
- proof pack
- replay instructions

## Replay Standard

Verification must validate the actual operation semantics or pinned fixture
content. Shape checks and hash-presence checks are not enough.

Civil proof-supported operations:

- `convert_bs_to_ad`
- `ad_to_bs`
- `validate_bs_date`
- `holiday`
- `working_day`
- `fiscal_year`
- `bs_months`

Panchanga proof-supported operation:

- `panchanga_summary`

## Local Verification

```bash
py -3.11 scripts/release/generate_proof_fixtures.py
py -3.11 -m pytest tests/integration/test_shared_proof_fixtures.py -q
cd packages/parva-local-kernel
npm install
npm test
```

Proof mode is an engineering verification mechanism. It is not government,
legal, tax, payroll, banking, religious, ritual, official future-date, or
official Panchanga authority.
