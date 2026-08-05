---
status: public-preview
tier: 2
lane: public-preview
last_verified: 2026-08-05
owner: research-team
---

# Future BS v7 Forecast Freeze

Project Parva v7 is frozen as `parva_future_bs_v7_2026-08-05`. The freeze records the model identity, training cutoff, public forecast snapshot, source commit, per-year commitments, and the rules for later scoring.

## Locked Baseline

- model: `parva_authority_aware_solar_civil_v7`
- training cutoff: BS 2083
- forecast range: BS 2084-2200
- model source commit: `0591ca687b3c91918d1c7557d5033f49d41ba248`
- snapshot SHA-256: `b02797b5074322e0856187daf3eb784142e8778adc031bcfc7b46ce0006112d9`
- yearly commitment Merkle root: `5f27afa2349e0e2ce20e97d31a0b5715eeec64c2e8d43d2a70e914fd2e377206`
- publication status: `computed_prediction_not_official`

The committed BS 2084 month vector is:

```text
31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30
```

Any change to the model or forecast requires a new model version and freeze ID. Updating v7 in place would break the integrity gate.

## Integrity Check

```bash
python scripts/future_bs/freeze_public_v7.py --check
```

CI and the public verification script run this command. It checks the forecast, model metadata, source hashes, commitment tree, evaluation protocol, and ledger event against the committed freeze.

## Prospective Score

When an authoritative BS calendar is published after the freeze, two reviewers independently extract its twelve month lengths. The reviewed source file stays in a private quarantine directory. Its hash, public URL, publication time, retrieval time, and reviewer identifiers go into a truth JSON file conforming to `data/future_bs/public/frozen/v7/prospective_truth.schema.json`.

```bash
python scripts/future_bs/score_frozen_forecast.py \
  --truth <reviewed-official-truth.json> \
  --output <prospective-score.json>
```

The scorer rejects pre-freeze publications, missing source files, hash mismatches, a single reviewer, invalid year totals, and any snapshot that differs from the frozen yearly commitment.

## Evidence Boundary

The 72 official months from BS 2078-2083 are a chronological development-window replay. Historical month values through BS 2083 also influenced the broader reference tower or model design. They therefore remain retrospective evidence.

BS 2084 is the first primary prospective test for this freeze. Its result becomes evidence after an authoritative calendar is published and reviewed. A single year will measure that year; it will not establish a broad accuracy guarantee.
