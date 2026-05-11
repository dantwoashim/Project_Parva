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
- Prohibited public claim and client-specific phrase grep across frontend public source.
- Edited redesign source grep for raw evidence labels, joined text, and mojibake patterns.

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

## Loop 2 - Browser Inspection, Public Landing, And Test Repair

Status: built, browser-inspected, linted, and tested locally.

Inspected:
- Routes: `/`, `/today`, `/my-place`, `/panchanga`, `/festivals`, `/best-time`, `/birth-reading`, `/trust`, `/methodology`, `/policy`, `/pricing`, `/developers`, `/enterprise`, `/future-bs`
- Viewports: `360x800`, `390x844`, `768x1024`, `982x1285`, `1024x768`, `1280x800`, `1440x900`
- Screenshot set: `tmp/ui-screenshots/loop-4`
- Browser audit data: `tmp/ui-screenshots/loop-4/inspection.json`

Broken:
- `/` still behaved like the daily product page instead of a public infrastructure landing page.
- `/best-time` exposed visible `Pending` labels in the broad smoke check.
- Mobile context cards had joined text such as `Today2026`.
- Today mobile hero showed a joined location/action label.
- My Place mobile copy visually joined words in the main explanation.
- Tests and visual snapshots still expected the older daily homepage and old Today heading.
- `git push origin main` failed because the configured GitHub credential is invalid.

Changed:
- Added a public infrastructure homepage at `/`.
- Added public-safe `/developers`, `/enterprise`, and `/future-bs` routes.
- Updated brand links to return to `/`.
- Added developer, enterprise, and future-BS research route metadata.
- Added responsive landing-page CSS for infrastructure cards, proof panel, and public CTAs.
- Removed visible `Pending` labels from Best Time selected-window defaults.
- Fixed mobile context card spacing and mobile nav wrapping.
- Hid Today mobile location action to avoid cramped duplicate context.
- Replaced visible em dash fallbacks in frontend source with plain text.
- Updated App route, consumer interaction, and visual regression tests for the new public positioning.
- Updated visual snapshots intentionally after verifying the new UI state.

Files changed:
- `frontend/src/App.jsx`
- `frontend/src/redesign/ParvaRedesign.jsx`
- `frontend/src/redesign/ParvaRedesign.css`
- `frontend/src/components/Festival/FestivalCard.css`
- `frontend/src/components/Festival/FestivalCard.jsx`
- `frontend/src/components/Festival/RitualTimeline.jsx`
- `frontend/src/components/Compass/OrbitalRing.jsx`
- `frontend/src/components/Compass/HorizonStrip.jsx`
- `frontend/src/styles/interactions.css`
- `frontend/src/test/AppRoutes.test.jsx`
- `frontend/src/test/ConsumerInteractions.test.jsx`
- `frontend/src/test/visual/VisualRegression.test.jsx`
- `frontend/src/test/visual/__snapshots__/VisualRegression.test.jsx.snap`

Commands run:
- `npm --prefix frontend run build`
- Playwright viewport smoke inspection against local Vite preview
- `npm --prefix frontend run lint`
- `npm --prefix frontend run test -- -u`
- `npm --prefix frontend run test`
- Public safety greps for old Cloud Run URLs, client-specific terms, prohibited public claims, and em dashes

Result:
- Build passed.
- Browser inspection found 0 issues across 42 route/viewport checks.
- Lint passed.
- Frontend tests passed: 24 test files, 109 tests.
- Old Cloud Run grep passed for frontend and `.env.example`.
- Public frontend source em dash grep passed after replacing visible fallbacks.

Commits:
- First priority commit: `be0fcd8` (`fix: stabilize public UI layout and API base`)
- Second loop commit: committed locally in the latest UI hardening commit.

Push status:
- Push attempted with normal Git credentials and failed.
- Push attempted with the provided token and failed with invalid credentials.
- Local commits are safe; remote push needs a valid GitHub credential.

Remaining issues:
- Remote push is blocked by invalid GitHub authentication.
- Render and Cloudflare environment variables still need to be set in the platforms after the code lands remotely.
