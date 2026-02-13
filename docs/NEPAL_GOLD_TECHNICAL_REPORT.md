# Nepal Gold Technical Report (Year 1)

## 1. Executive Summary

Project Parva Year 1 delivers a unified V2 calendar engine with rule-based festival calculation, ephemeris-backed panchanga endpoints, and provenance metadata for verification.

Key results:
- Single-engine enforcement on v2 routes.
- Versioned API contract with deprecation path for legacy routes.
- Explainability endpoint for festival date reasoning.
- Reproducible evaluation pipeline and scorecard tracking.

## 2. System Architecture

### 2.1 Layers
- Frontend: React + Vite
- API: FastAPI (`/v2/api/*`)
- Engine: BS conversion, tithi/panchanga, festival rule engine
- Data: festival corpus, normalized sources, ground truth, rule sets

### 2.2 Contract Evolution
- Legacy: `/api/*`
- Stable: `/v2/api/*`
- Deprecation headers on legacy (`Deprecation`, `Sunset`, `Link`).

## 3. Core Algorithms

### 3.1 BS Conversion (dual mode)
- `official` mode in validated lookup range.
- `estimated` mode outside official lookup range.
- Response includes `confidence`, `source_range`, `estimated_error_days`.

### 3.2 Tithi and Panchanga
- Udaya tithi preferred (`ephemeris_udaya`) when sunrise computation succeeds.
- Fallback path marked as `instantaneous` with lower confidence.
- Panchanga endpoint returns astronomical confidence metadata.

### 3.3 Festival Rule Resolution
- Rule types: lunar, solar, fallback.
- Explain endpoint reports rule summary + decision steps.

## 4. Data Pipeline

### 4.1 Inputs
- Festival corpus (`data/festivals/festivals.json`)
- OCR/normalized source tables (`data/normalized_sources.json`)
- Ground truth discrepancy register (`data/ground_truth/discrepancies.json`)

### 4.2 Pipeline Commands
- `./scripts/annual_rerun.sh`
- `PYTHONPATH=backend python3 backend/tools/evaluate_v4.py`
- `python3 backend/tools/triage_mismatches.py`

## 5. Provenance and Trust

### 5.1 Snapshot Hashing
- Dataset and rules hashed with deterministic SHA-256 canonicalization.
- Snapshot records stored at `backend/data/snapshots/`.

### 5.2 Merkle Verification
- Festival-date snapshot leaves are merkleized for proof generation.
- Query endpoint supports inclusion proof retrieval and verification.

### 5.3 Response Metadata
Date-bearing endpoints now include:
- `provenance.dataset_hash`
- `provenance.rules_hash`
- `provenance.snapshot_id`
- `provenance.verify_url`

## 6. Testing and Quality Gates

### 6.1 Automated Tests
- `223` tests passing in current baseline.
- Contract tests for v2 routing and deprecation behavior.
- Integration tests for explainability endpoint.

### 6.2 Runtime Checks
- v2 E2E smoke: `9/9` endpoints pass.
- In-process load test (100 concurrent): 0% error rate on baseline run.

## 7. Evaluation Results

Current benchmark summary (from `reports/evaluation_v4/evaluation_v4.json`):
- Total: 40
- Passed: 40
- Failed: 0
- Pass rate: 100%

## 8. Known Limitations

- Official-vs-estimated conversion behavior must remain explicitly documented for out-of-range years.
- Merkle proofs verify snapshot inclusion, not semantic correctness of source data.
- Regional observance variants are only partially modeled in current rule corpus.

## 9. Reproducibility Instructions

```bash
# Full benchmark package
./benchmark/run_benchmark.sh

# Full test suite
python3 -m pytest -q

# Frontend production build
cd frontend && npm run build
```

## 10. Conclusion

Year 1 establishes Project Parva as a technically verifiable, contract-stable festival computation platform with transparent date reasoning and reproducible validation workflows.
