# Calendar evidence

Reviewed on 14 November 2026. Source references use physical PDF page numbers, starting at 1. Archived documents are in `data/source_archive/moha/` at the repository root; their SHA-256 hashes are recorded in `src/parva/data/SOURCES.json`.

## Corrections

| Record | Corrected interpretation | Source |
| --- | --- | --- |
| BS 2083 Dashain closure | Ashwin 31 through Kartik 6, inclusive: 7 days | 2083 PDF, p. 2 |
| BS 2083 Tihar closure | Kartik 22 through 26, inclusive: 5 days | 2083 PDF, pp. 2–3 |
| BS 2082 Dashain / Tihar | Ashwin 13–18: 6 days; Kartik 3–7: 5 days | 2082 PDF, p. 2 |
| BS 2083 Saraswati Puja | Schools, not a national office closure | 2083 PDF, p. 4 |
| BS 2083 Jitiya | Women observing Jitiya, not all women | 2083 PDF, p. 4 |
| BS 2083 Gaura | Relevant community, not an inferred province-wide closure | 2083 PDF, p. 4 |
| BS 2083 Gai Jatra | Newar community and Kathmandu Valley scopes | 2083 PDF, pp. 4–5 |
| BS 2083 Yomari / Dhanya Purnima / Udhauli | National scope in this notice | 2083 PDF, p. 3 |
| Civil Service Day / Gen Z Martyrs Day | Section 8 observances with offices open in this annual baseline; later amendments are not incorporated | 2083 PDF, p. 6 |
| Previously missing 2083 entries | Labour Day, Republic Day, Disability Day, Prithvi Jayanti, Maghe Sankranti, International Women's Day, hill and Terai Holi dates | 2083 PDF, pp. 3, 5–6 |

The machine-readable correction ledger is in `src/parva/data/release.json`. Existing source text is retained. Added English transcriptions are explicitly labeled as transcriptions, not verbatim quotations.

## Review states

- `source_checked`: date, scope and closure interpretation compared with the archived page image.
- `weekday_checked`: imported date passed an earlier weekday comparison; scope and duration may still need review.
- `pending`: no sufficient source review recorded.

All 36 BS 2083 records and two BS 2082 holiday blocks have source-page references. Other historical entries are preserved for comparison and remain unreviewed at source-page level. Older assumed spans are labeled and excluded from calendar subscriptions and definitive working-day decisions.

No year is complete. Eid, Bakr Eid and some local or community holidays in the notices do not have fixed dates. Later notices can change the annual baseline. A positive source match can establish a closure under the selected scope; absence from these records cannot establish an ordinary working day.

## Conversion evidence

The table covers BS 2000–2095 and is anchored at 2082-01-01 BS = 2025-04-14 AD. Structural and exhaustive round-trip checks detect implementation inconsistencies. The preserved reference fixture agrees on 72 month lengths for BS 2078–2083, but its historical label `official_holdout` should not be read as a new independent holdout study. Source-backed holiday dates provide additional spot checks, not independent verification of every month.

BS 2084–2095 remains provisional. The table is not regenerated from the astronomical forecast research. The BS 2087 row uses the community 366-day row; a prior 367-day row was excluded from the candidate.

## Updating records

Change only the affected JSON rows, add the source hash and page, and record the correction in `release.json`. Run `tools/verify_data.py` and the regression suite. A newly imported row is a candidate until its scope, inclusive endpoints and closure status have been checked. Never infer a missing span from another year.
