# Optional JPL Kernel Setup for Panchanga Replay

Parva does not bundle large JPL ephemeris kernels. The default public lane uses
pinned fixtures or the built-in fallback provider and must not be described as
JPL-backed.

To enable the optional local JPL metadata/replay lane, place a legally obtained
kernel on your machine and set:

```bash
PARVA_JPL_KERNEL_PATH=/absolute/path/to/de440.bsp
PARVA_JPL_KERNEL_SHA256=sha256:<expected kernel hash>
```

The provider will:

- verify that the configured kernel exists,
- compute and compare its SHA-256 hash when `PARVA_JPL_KERNEL_SHA256` is set,
- disclose provider id, ephemeris version, kernel hash, supported-range note,
  and non-authority boundary metadata,
- fail instead of silently falling back if the configured kernel hash does not
  match.

If no kernel path is configured, optional JPL tests are skipped and public
verification continues with pinned fixtures/fallback computation. That skipped
state is not external validation and not official Panchanga authority.
