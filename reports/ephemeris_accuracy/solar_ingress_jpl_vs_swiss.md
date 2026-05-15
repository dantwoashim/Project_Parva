# Solar Ingress JPL vs Swiss

Status: public generated artifact.

The JPL integration layer is present as an optional research adapter and a hash
verified kernel policy. Public verification does not require JPL kernels and
must continue to pass with the public fallback.

Current report posture:

- JPL/DE440 role: high-precision astronomical cross-check.
- Swiss/Moshier role: public fallback for default verification.
- Public exact Future-BS output: not exposed.
- Kernel paths: omitted by policy.
- Civil authority: not claimed.

Full differential rows should be generated only in a private or research
operator environment after `python scripts/ephemeris/verify_kernel_hashes.py`
passes.
