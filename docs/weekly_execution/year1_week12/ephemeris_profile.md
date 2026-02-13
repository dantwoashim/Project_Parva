# Ephemeris Performance Profile (Week 12)

Run size: 500 calls to `get_sun_moon_positions`

- Average: 0.025 ms
- Median: 0.014 ms
- P95: 0.016 ms
- P99: 0.019 ms
- Max: 5.351 ms

Conclusion: ephemeris calls are comfortably below a 50ms per-call budget.
