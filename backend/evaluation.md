# Discrepancy Analysis

**Evaluation Date**: 2026-02-06

**Total Cases**: 20  
**Passed**: 8  
**Failed**: 12

## ❌ Failed Cases

| Festival | Year | Expected | Calculated | Variance | Source | Error |
|----------|------|----------|------------|----------|--------|-------|
| buddha-jayanti | 2026 | 2026-05-12 | 2026-05-30 | 18d | nepal_gov | variance |
| janai-purnima | 2026 | 2026-08-11 | 2026-07-28 | 14d | nepal_gov | variance |
| teej | 2026 | 2026-08-30 | 2026-08-14 | 16d | nepal_gov | variance |
| indra-jatra | 2026 | 2026-09-08 | 2026-08-23 | 16d | nepal_gov | variance |
| gai-jatra | 2026 | 2026-08-12 | 2026-07-29 | 14d | nepal_gov | variance |
| yomari-punhi | 2026 | 2026-12-25 | 2026-12-23 | 2d | estimated | variance |
| mha-puja | 2026 | 2026-11-11 | 2026-11-08 | 3d | estimated | variance |
| chhath | 2026 | 2026-11-12 | 2026-10-15 | 28d | estimated | variance |
| maghe-sankranti | 2027 | 2027-01-14 | 2027-01-16 | 2d | estimated | variance |
| holi | 2027 | 2027-03-22 | 2027-02-20 | 30d | estimated | variance |
| dashain | 2025 | 2025-10-20 | 2025-09-21 | 29d | nepal_gov_2025 | variance |
| tihar | 2025 | 2025-10-28 | 2025-10-19 | 9d | nepal_gov_2025 | variance |

### Analysis


**Variance Failures**: 12 cases outside acceptable range

- `buddha-jayanti` (2026): 18 day(s) off
- `janai-purnima` (2026): 14 day(s) off
- `teej` (2026): 16 day(s) off
- `indra-jatra` (2026): 16 day(s) off
- `gai-jatra` (2026): 14 day(s) off
- `yomari-punhi` (2026): 2 day(s) off
- `mha-puja` (2026): 3 day(s) off
- `chhath` (2026): 28 day(s) off
- `maghe-sankranti` (2027): 2 day(s) off
- `holi` (2027): 30 day(s) off
- `dashain` (2025): 29 day(s) off
- `tihar` (2025): 9 day(s) off
