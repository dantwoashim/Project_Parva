# Panchanga JPL Lane Report

This report does not claim official Panchanga or ritual authority. Real JPL execution is claimed only when a configured kernel is available and hashed.

- Status: configured
- Real JPL kernel claimed: True
- Skip reason: none
- JPL provider available: True
- JPL kernel hash: sha256:a4ce9bf9b3282becc9f4b2ac3cebe03a2ae7599981aabd7265fd8482fff7c4b5
- Fallback provider: builtin_swiss_moshier
- Fallback claims JPL: False

To run the optional real-kernel lane, set `PARVA_JPL_KERNEL_PATH` and optionally `PARVA_JPL_KERNEL_SHA256`, then run `pytest tests/integration/test_jpl_provider_optional.py -q`.
