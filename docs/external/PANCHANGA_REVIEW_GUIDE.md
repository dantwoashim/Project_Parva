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

The repository uses a pinned fixture slice for deterministic tests and exposes a
JPL provider interface for locally configured kernels. It does not bundle large
JPL kernels and does not claim official Panchanga or ritual authority.
