# BS Conversion Comparison (Official vs Estimated)

**Scope:** Official lookup overlap years `2070–2095 BS`  
**Method:** Compare official lookup conversion against the sankranti‑based estimated conversion

## Summary

- **Total days compared:** 9,498  
- **Matches:** 4,851  
- **Mismatches:** 4,647  
- **Match rate:** **51.0739%**

## Interpretation

The sankranti‑based estimated conversion does **not** match the official BS lookup table for a large portion of dates.  
This indicates that the official BS calendar uses **committee‑defined month length tables** that cannot be reproduced purely from solar transits.  
Therefore:

- **Lookup table is authoritative** within the official range.  
- **Estimated conversion is only a best‑effort approximation** for past/future years where tables are unavailable.  
- The API now returns **`confidence = "official"`** for lookup dates and **`"estimated"`** for computed dates.

## First 10 Mismatches (Example)

| Gregorian Date | Official BS | Estimated BS |
|---|---|---|
| 2013-04-13 | 2070-01-01 | 2069-12-30 |
| 2013-04-14 | 2070-01-02 | 2070-01-01 |
| 2013-04-15 | 2070-01-03 | 2070-01-02 |
| 2013-04-16 | 2070-01-04 | 2070-01-03 |
| 2013-04-17 | 2070-01-05 | 2070-01-04 |
| 2013-04-18 | 2070-01-06 | 2070-01-05 |
| 2013-04-19 | 2070-01-07 | 2070-01-06 |
| 2013-04-20 | 2070-01-08 | 2070-01-07 |
| 2013-04-21 | 2070-01-09 | 2070-01-08 |
| 2013-04-22 | 2070-01-10 | 2070-01-09 |

## Conclusion

For **200‑year past/future support**, the most accurate approach is:

1. **Use official lookup tables whenever available** (authoritative).  
2. **Use ephemeris + sankranti estimation outside the lookup range**, with explicit `confidence = "estimated"`.  

If full official accuracy is required for the 200‑year span, the only reliable option is to **acquire or digitize official BS tables** for that span and store them as lookup data.

