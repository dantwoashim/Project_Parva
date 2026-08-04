# IRD Software Vendor Prospect Set

## Purpose

This file accompanies `ird_vendor_prospects_2026.csv`. It contains 50 distinct
PAN-level prospects selected for a Parva BS Date Risk Audit and annual date
assurance offer.

## Source

- Publisher: Inland Revenue Department, Government of Nepal
- Registry: Computer Billing List under the Electronic Billing Procedure
- Source URL: `https://www.ird.gov.np/public/pdf/501426892.pdf`
- Source snapshot: search-indexed copy crawled approximately six months before
  2026-08-04, containing entries through at least S.N. 1368
- Extraction date: 2026-08-04

The live PDF URL returned HTTP 404 during extraction. Every prospect therefore
requires a fresh registry check before outreach. The CSV preserves S.N., PAN,
application version, enlisted number, PDF page, and declared technology so each
row can be reconciled when IRD republishes the list.

## Selection Rules

- One prospect per PAN.
- Priority for ERP, accounting, billing, POS, healthcare, distribution, and
  localization products with recurring BS, fiscal, invoice, or scheduling work.
- Preference for recent registry rows and maintained technology stacks.
- Exclusion of obvious malformed test rows, duplicate versions, customer-only
  SAP or Dynamics installations, and applications without a clear temporal use.
- Application names are registry labels. They are not assumed to be legal
  company names.
- No contact details were guessed. Contact discovery should match the
  application name and PAN before any message is sent.

## Priority

- Priority A: first 20 prospects. Start with a tailored technical message and a
  free twenty-case audit.
- Priority B: remaining 30 prospects. Use after the first pilot report is ready.

The strongest opening proof is the merged source-consistency benchmark in Yarsa
Labs' Nepal Compliance repository. It demonstrates accepted upstream work; it
does not represent endorsement or certification.

## Outreach Workflow

1. Verify the application and PAN against the current IRD publication.
2. Find the product owner, founder, CTO, or engineering lead from a first-party
   website or company profile.
3. Inspect a public demo, documentation page, or API before writing.
4. Mention one concrete workflow: invoice date, payroll cutoff, fiscal boundary,
   POS day-close, appointment, or repayment date.
5. Offer the sanitized twenty-case audit and request output data only. Production
   database access is unnecessary.
6. Record response, next action, and verification date outside the public source
   file.
