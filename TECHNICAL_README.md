# Project Parva - Technical Documentation

> Nepal Festival Discovery System with Astronomical Accuracy

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## API Endpoints

### Calendar

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/calendar/convert` | GET | Convert date to BS/NS/Tithi |
| `/api/calendar/today` | GET | Today's calendar info |
| `/api/calendar/panchanga` | GET | Full 5-element panchanga |
| `/api/calendar/festivals/calculate/{id}` | GET | Calculate festival date |

### Provenance

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/provenance/root` | GET | Merkle root + hash |
| `/api/provenance/verify/{id}` | GET | Verify festival with proof |

---

## Core Algorithms

### Festival Calculation (calculator_v2.py)

```python
# Uses lunar month model for Adhik Maas handling
from app.calendar.calculator_v2 import calculate_festival_v2

result = calculate_festival_v2("dashain", 2026)
# Returns: FestivalResult(start_date=2026-09-12, ...)
```

### Tithi Calculation (tithi.py)

```python
from app.calendar.tithi import get_udaya_tithi

udaya = get_udaya_tithi(date(2026, 2, 15))
# Returns: {"tithi": 14, "paksha": "krishna", "name": "Chaturdashi"}
```

### Merkle Verification (merkle.py)

```python
from app.calendar.merkle import get_festival_proof, MerkleTree

proof = get_festival_proof(path, 2026, "dashain")
verified = MerkleTree.verify_proof(proof.leaf_hash, proof.proof, proof.root)
```

---

## Data Files

| File | Location | Purpose |
|------|----------|---------|
| `festival_rules_v3.json` | `app/calendar/` | Festival definitions |
| `snapshot.json` | `data/` | Canonical dates 2024-2030 |
| `snapshot_hash.txt` | `data/` | SHA-256 hash |
| `seph/*.se1` | `app/calendar/ephemeris/` | Swiss Ephemeris data |

---

## Performance

- **P95 Latency**: 6.9ms
- **Throughput**: 338 ops/sec
- **Festivals**: 21
- **Test Coverage**: 55 tests passing

---

## Development

```bash
# Run tests
pytest tests/ -v

# Run evaluation
python tools/evaluate_v3.py

# Generate snapshot
python tools/generate_snapshot.py
```

---

## Architecture

See [architecture.md](architecture.md) for system design.

## Security

See [security_checklist.md](security_checklist.md) for deployment guidelines.
