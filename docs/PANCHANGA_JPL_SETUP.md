# Optional JPL Kernel Metadata Setup

Parva does not bundle large JPL ephemeris kernels. The default public lane uses
pinned fixtures or the built-in fallback provider and must not be described as
JPL-backed.

To enable the optional local JPL metadata lane, place a legally obtained
kernel on your machine and set:

```bash
PARVA_JPL_KERNEL_PATH=/absolute/path/to/de440.bsp
PARVA_JPL_KERNEL_SHA256=sha256:<expected kernel hash>
PARVA_JPL_KERNEL_SIZE=<expected byte size>
```

The provider will:

- verify that the configured kernel exists,
- require and compare its SHA-256 hash,
- validate its DAF/SPK structure and Sun/Earth/Moon segment coverage,
- disclose metadata-only provider identity, kernel hash, segment count, and
  non-authority boundary metadata,
- fail instead of silently falling back if the configured kernel hash does not
  match.

This setup does not enable a JPL Panchanga calculation provider. The
`jpl_de440` calculation id remains unavailable until an independent calculation
backend is implemented and validated.

If no kernel path is configured, optional JPL tests are skipped and public
verification continues with pinned fixtures/fallback computation. That skipped
state is not external validation and not official Panchanga authority.
