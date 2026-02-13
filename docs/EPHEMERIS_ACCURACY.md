# Ephemeris Accuracy & Verification (Week 11)

## Verification Assets
- Fixture: `tests/fixtures/ephemeris_500.json`
- Test: `tests/unit/engine/test_ephemeris_500.py`
- Generator: `backend/tools/generate_ephemeris_fixture.py`

## Coverage
- 500 deterministic UTC timestamps
- Range: 2000-2100 AD
- Metrics validated:
  - Sun longitude tolerance: <= 0.01°
  - Moon longitude tolerance: <= 0.05°

## Purpose
This is a regression verification layer to detect implementation drift in astronomical calculations.

## Runtime Mode
- Ephemeris: Swiss/Moshier (pyswisseph)
- Coordinate system: Sidereal (default)
- Ayanamsa: Lahiri (default)
