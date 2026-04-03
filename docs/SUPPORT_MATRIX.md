# Support Matrix

Project Parva exposes multiple temporal subsystems with different evidence models. This matrix defines how each subsystem should be interpreted in the public product and API.

## Support Tiers

- `authoritative`: Directly backed by official overlap tables or explicit authority-selected override records.
- `computed`: Derived from the canonical engine path with stable assumptions and no active authority conflict.
- `heuristic`: Computed output is usable, but defaults, provisional bands, or weaker evidence make it less trustworthy than the canonical computed path.
- `estimated`: Output extends beyond the strongest support zone or depends on explicitly estimated logic.
- `conflicted`: Multiple authority-backed candidates exist and the public default is a policy selection, not a universally uncontested date.
- `abstained`: Reserved for future strict/risk-coverage modes where the engine chooses not to force a weak answer.

## Product Scope

| Surface | Primary engine path | Current public support | Notes |
| --- | --- | --- | --- |
| BS/AD conversion | Official overlap tables plus bounded estimated fallback | `authoritative` inside official support zone, `estimated` outside it | Preserve `support_tier`, `method`, and `quality_band` when storing results. |
| Panchanga / tithi | Swiss Ephemeris sunrise-based calculation | `computed` by default, `heuristic` when defaults or provisional bands apply | Location and timezone defaults reduce support tier even when output remains deterministic. |
| Festival dates | Rule engine plus authority-aware override selection | `authoritative`, `computed`, `conflicted`, or `estimated` depending on source state | Festival detail and explain routes also expose `selection_policy`, `alternate_candidates`, and `source_family`. |
| Muhurta | Ranked daily windows from canonical muhurta engine | `computed` by default | Treat as ritual-planning assistance, not civil authority. |
| Kundali | Deterministic Swiss Ephemeris sidereal charting | `computed` by default | Tradition-scoped computational aid; not a scientific truth claim. |
| Place search | Offline Nepal gazetteer when possible, remote geocoder fallback otherwise | `computed` by default | Privacy posture depends on `source_mode`; remote lookups remain explicit. |

## Public API Contract

Every temporal response should expose these fields:

- `support_tier`
- `engine_path`
- `fallback_used`
- `calibration_status`

Festival detail and explain responses must additionally expose:

- `selection_policy`
- `authority_conflict`
- `alternate_candidates`
- `source_family`

## Interpretation Rules

- `engine_path` identifies the concrete computation path used for the current response.
- `fallback_used` is reserved for legacy or fallback computation activation, not for input defaulting alone.
- `calibration_status="unavailable"` means the route does not currently have an empirical calibration artifact behind its confidence wording.
- `calibration_status="not_applicable"` is used where empirical calibration is not the right abstraction, such as explicit authority-selected override results.
- `quality_band` and `support_tier` are related but not identical:
  - `quality_band` is a route- or dataset-facing maturity band.
  - `support_tier` is the public trust posture for the specific response.

## Known Limits

- Festival conflicts can still occur across authority families; `public_default` is the stable product policy, not proof that all sources agree.
- Personal routes may remain deterministic while still dropping to `heuristic` if location or timezone defaults were applied.
- Kundali and muhurta outputs should be presented as deterministic tradition-scoped assistance, not scientific validation.
- Future strict-mode abstention and risk-coverage outputs are planned but not yet the default product behavior.
