# Sunrise Method & Accuracy Notes

- Method: Swiss Ephemeris `rise_trans` with Kathmandu defaults.
- Representation:
  - internal: UTC
  - API display: Nepal time (`UTC+05:45`)
- Regression corpus:
  - file: `tests/fixtures/sunrise_kathmandu_50.json`
  - test: `tests/unit/engine/test_sunrise_kathmandu.py`
  - tolerance: <= 60 seconds

This corpus is used as deterministic regression protection for future refactors.
