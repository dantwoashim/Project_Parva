# Panchanga JPL Lane Report

This report does not claim official Panchanga or ritual authority. Real JPL execution is claimed only when a configured kernel is available and hashed.

- Status: skipped
- Real JPL kernel claimed: False
- Skip reason: The committed public report does not use local JPL environment variables; default proof lane uses pinned fixtures and fallback metadata only. Run with --use-configured-jpl for a local real-kernel trial.
- JPL provider available: False
- JPL kernel hash: not configured
- Fallback provider: builtin_swiss_moshier
- Fallback claims JPL: False

To run the optional real-kernel lane, set `PARVA_JPL_KERNEL_PATH` and optionally `PARVA_JPL_KERNEL_SHA256`, then run `pytest tests/integration/test_jpl_provider_optional.py -q`.
