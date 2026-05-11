# UI Surgical Audit

This file records the public frontend hardening loops. It is public-safe and does not include private future-BS values, client-specific details, or private model internals.

## Loop 1 - Header, API Base, And Primary Cards

Status: built locally, ready for first priority commit.

Inspected:
- `frontend/src/redesign/ParvaRedesign.jsx`
- `frontend/src/redesign/ParvaRedesign.css`
- `frontend/src/services/api.js`
- `frontend/src/services/apiCore.js`
- `frontend/index.html`
- `.env.example`

Broken:
- Header actions, place context, search, and profile controls competed for the same row at compact desktop widths.
- Frontend API base still allowed split `VITE_API_BASE_URL` behavior instead of a single public Render API base.
- Today cards used vague labels like `Answer` and `Action`.
- Primary UI exposed raw-style evidence references.
- My Place search lacked a clear helper and looked detached.
- API timeout/network errors did not explain Render cold starts.

Changed:
- Added `frontend/src/services/apiBase.js` and routed frontend API clients through one central API base resolver.
- Set `.env.example` to use `VITE_API_BASE=https://api.prabinghimire1.com.np/v3/api`.
- Added CORS examples for the public domain, `www`, and Cloudflare Pages preview domain.
- Added final CSS overrides that hide orphan profile/place header controls, keep search and trust compact, and move date/place/search into a controlled context bar.
- Updated Today hero and verification cards to clearer infrastructure language.
- Replaced raw evidence references in primary cards with human-readable `View evidence` / `Calculation evidence`.
- Added cold-start retry guidance to user-facing API errors.
- Added a clear My Place search placeholder and helper.
- Updated frontend meta tags and route SEO to position Parva as Nepali temporal infrastructure.

Files changed:
- `.env.example`
- `frontend/index.html`
- `frontend/src/App.jsx`
- `frontend/src/redesign/ParvaRedesign.css`
- `frontend/src/redesign/ParvaRedesign.jsx`
- `frontend/src/services/api.js`
- `frontend/src/services/apiCore.js`
- `frontend/src/services/apiBase.js`
- `frontend/src/services/errorFormatting.js`

Commands run:
- `npm --prefix frontend run build`
- `rg -n "project-parva-api|run\.app|asia-south1" frontend .env.example -S --glob '!**/node_modules/**' --glob '!**/dist/**' --glob '!**/build/**'`
- `rg -n "InfoDevelopers|infodev|cracked Panchanga|guaranteed future|official future calendar|99% future accuracy" frontend -S --glob '!**/node_modules/**' --glob '!**/dist/**' --glob '!**/build/**'`
- `rg -n "Evidence [A-Za-z0-9_:-]|Ref [A-Za-z0-9_:-]|Plan or subscribe|Astronomical signal|Kathmandu, NepalMay|Â·|Â°|â|Ã" frontend/src/redesign/ParvaRedesign.jsx frontend/src/redesign/ParvaRedesign.css -S`

Result:
- Frontend build passed.
- No old Cloud Run references found in frontend or `.env.example`.
- No client-specific or prohibited claim phrases found in frontend.
- No primary-card raw evidence patterns or mojibake patterns found in the edited redesign source/CSS grep.

Commit:
- Pending at the time this audit entry was written.

Remaining issues:
- Need browser viewport inspection across 360, 390, 768, 982, 1024, 1280, and 1440 widths.
- Need inspect `/`, `/today`, `/my-place`, `/panchanga`, `/festivals`, `/best-time`, `/birth-reading`, `/trust`, `/methodology`, `/policy`, and `/pricing`.
- Need decide whether to add or route lightweight public `/developers`, `/enterprise`, and `/future-bs` pages.
- Need run or add smoke tests for header overflow and horizontal scroll.
