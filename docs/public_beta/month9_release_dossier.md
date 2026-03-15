# Month 9 Release Dossier (Public Beta)

Generated at: `2026-03-14T09:22:29.711845+00:00`

## Coverage Scoreboard

| Metric | Value |
|---|---:|
| Computed Rules | 323 |
| Provisional Rules | 111 |
| Inventory Rules | 19 |
| Safe To Claim 300 | True |

## Plugin Quality (Parity)

| Plugin | Cases | Pass Rate | Quality Band | Within Error Budget |
|---|---:|---:|---|---|
| bs | 7 | 100.0% | gold | True |
| chinese | 7 | 100.0% | gold | True |
| hebrew | 7 | 100.0% | gold | True |
| islamic | 7 | 100.0% | gold | True |
| julian | 7 | 100.0% | gold | True |
| ns | 7 | 100.0% | gold | True |
| tibetan | 7 | 100.0% | gold | True |

## Personal Stack Methodology

| Module | Method Profile | Quality | Assumption Set | Advisory Scope |
|---|---|---|---|---|
| Personal Panchanga | personal_panchanga_v2_udaya | gold | np-personal-panchanga-v2 | ritual_planning |
| Muhurta | muhurta_v2_hora_chaughadia_tarabala | validated | np-mainstream-v2 | ritual_planning |
| Kundali | kundali_v2_aspects_dasha | validated | np-kundali-v2 | astrology_assist |

## Known Limits

- Regional observance jurisprudence can differ by tradition; API output is profile-based, not absolute religious authority.
- Some festival entries remain provisional and rely on source curation before being promoted to fully computed status.
- Very fine boundary cases near sunrise can vary when location/timezone inputs differ.
- Personal Muhurta/Kundali outputs are informational and include policy advisories.
- Public API profile is v3; experimental routes may change without compatibility guarantees.
- Zero-budget hosting implies occasional cold-start latency on free tiers.
- Authority Mode exposes computation metadata; it is not a legal or doctrinal certification layer.
- Temporal Compass and ribbon views are optimized for modern browsers; older embedded webviews may degrade to basic card rendering.
- Visual regression snapshots are deterministic fixtures, not live observational truth data.
- This repository now uses the AGPL zero-budget path for Swiss Ephemeris / `pyswisseph`, so hosted commercial use remains possible only if users can access the corresponding deployed source.

## Evidence Artifacts

- `reports/conformance_report.json` (generated artifact)
- `reports/authority_dashboard.json` (generated artifact)
- `reports/accuracy/annual_accuracy_2082.json` (generated artifact)
- `data/festivals/festival_rules_v4.json`
