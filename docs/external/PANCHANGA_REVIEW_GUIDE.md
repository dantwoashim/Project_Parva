# Panchanga Review Guide

Panchanga outputs are computed and method-docketed. They must disclose:

- date
- location and timezone
- ayanamsa
- sunrise rule
- ephemeris provider
- ephemeris version and fixture/kernel hash where applicable
- method dockets
- non-authority boundaries

The repository uses a pinned fixture slice for deterministic tests. Locally
configured JPL files can be validated and disclosed as metadata, but they are
not selectable Panchanga calculation providers. The repository does not bundle
large JPL kernels and does not claim official Panchanga or ritual authority.
