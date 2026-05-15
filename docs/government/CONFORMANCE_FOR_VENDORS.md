# Conformance for Vendors

Vendor conformance should test whether software systems:

- reject invalid BS dates,
- preserve source metadata,
- preserve review-required behavior,
- separate holidays from working-day policies,
- separate panchanga computation from official authority,
- avoid exact unsupported Future-BS predictions,
- verify release checksums,
- handle unsupported ranges without guessing.

Passing a Parva conformance test is not a government certification. It is a
technical compatibility signal for a specific release format and test version.
