---
status: research
tier: 3
lane: research
last_verified: 2026-08-05
owner: research-team
---

# Official Calendar Acquisition Protocol

The acquisition program has two separate purposes: recover source lineage for historical BS values and preserve untouched official truth for forecasts that were recorded before publication. These purposes use different evidence labels and evaluation claims.

## Evidence Lanes

### Historical lineage

Annual calendars and dated records from BS 2000-2083 are used to verify where existing month lengths came from, locate transcription errors, and study civil month-start practice. Those values already influenced the reference table or model development. They support provenance audits and retrospective rolling replays.

### Prospective truth

Official calendars published after a forecast freeze are quarantined until their source file is hashed and two reviewers independently extract the month lengths. They are then scored once against the unchanged frozen forecast. BS 2084 is the first primary prospective year for v7.

## Source Classes

1. A complete annual government or NPNS calendar with visible BS and AD alignment can supply a full-year row after review.
2. A Nepal Gazette or Ministry of Home Affairs holiday notice supplies dated witnesses. It does not supply a complete month-length row by itself.
3. An identifiable printed Panchanga or Patro can supply reviewed evidence when its cover, publisher or colophon, year, relevant month pages, and next-year Baishakh 1 page are captured.
4. A government notice, court record, newspaper masthead, or institutional publication can corroborate individual AD and BS date pairs.
5. Software tables and commercial calendar sites remain comparison evidence unless their underlying authoritative source is recovered.

## Required Intake Record

Every acquired item records:

- source institution and document title
- BS year and covered months
- original public URL or physical archive identifier
- publication and retrieval timestamps
- raw-file SHA-256
- local quarantine path
- page numbers used for extraction
- extraction method and OCR status
- independent reviewer identifiers
- conflicts, corrections, and promotion status

Raw files enter an operator-created `source_quarantine` directory under `data/future_bs/private/`, which is excluded from the public repository. Public records contain source metadata and hashes. A source file may be published only when redistribution rights are clear.

## Review Procedure

1. Download or photograph the source without editing it.
2. Hash the original bytes before OCR or image processing.
3. Reviewer A extracts all month starts or month lengths.
4. Reviewer B repeats the extraction without seeing Reviewer A's values.
5. Resolve disagreements against the source pages and record the resolution.
6. Validate twelve months, allowed lengths of 29-32 days, and a 365- or 366-day total.
7. Mark the item as historical lineage or prospective truth before it enters any evaluation.
8. Preserve the original record and append corrections rather than overwriting audit history.

## Acquisition Order

The first pass repairs direct provenance for the current BS 2078-2083 official window. Older work then proceeds in ten-year bands: 2068-2077, 2058-2067, 2048-2057, and finally 2000-2047.

Priority channels are:

- Nepal Panchanga Nirnayak Samiti annual material
- Department of Information and Broadcasting table calendars
- Nepal Gazette and Ministry of Home Affairs annual holiday notices
- provincial and local government annual calendars
- National Archives, Nepal National Library, TU Central Library, and identifiable Panchanga publisher collections
- Gorkhapatra and other dated public records around disputed month boundaries

The public [source acquisition register](../../data/future_bs/public/official_source_acquisition_register_v1.json) records confirmed links, source roles, current gaps, and review state. Holiday notices for [BS 2079](https://www.moha.gov.np/post/this-information-has-been-published-as-the-government-of-nepal-has-decided-to), [BS 2080](https://www.moha.gov.np/post/public-holidays-for-2080-2), [BS 2081](https://www.moha.gov.np/post/government-and-public-holidays-in-2081-2), [BS 2082](https://www.moha.gov.np/en/post/government-and-public-holidays-in-2082-2), and [BS 2083](https://www.moha.gov.np/post/government-and-public-holidays-in-2083) are official witness channels. Their dates require extraction and review; the notices do not automatically become complete calendar rows.

## Promotion Gates

A source reaches `official_verified` only when its institution, original artifact, hash, coverage, and review record are complete. Automated discovery alone creates an acquisition candidate. OCR output alone creates a review candidate. Neither state changes model truth.

New historical evidence may feed a separately versioned research model. It cannot alter the frozen v7 forecast. New prospective truth is scored against v7 before it is eligible for any later training run.
