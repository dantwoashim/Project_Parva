# UI Release Checklist

## Current Status

Status: local public-release checks passed. Remote push is blocked by invalid GitHub credentials.

## Public Safety

- [x] Frontend API base uses Render public API through `VITE_API_BASE`.
- [x] No old Cloud Run URL references found in frontend or `.env.example`.
- [x] No client-specific references found in frontend.
- [x] Primary UI labels avoid raw evidence IDs.
- [x] Public copy added in this loop avoids official authority and guaranteed future accuracy claims.
- [x] Future-BS sensitive values were not added.

## Layout

- [x] Header actions simplified so profile/place controls no longer compete with nav.
- [x] Context controls moved into a controlled context bar.
- [x] Desktop viewport inspected in browser.
- [x] Tablet viewport inspected in browser.
- [x] Mobile viewport inspected in browser.
- [x] 982px compact desktop inspected in browser.
- [x] No horizontal scroll verified in browser.

## Pages

- [x] Today page copy and card labels cleaned.
- [x] My Place search helper added.
- [x] Panchanga page inspected in browser.
- [x] Festivals page inspected in browser.
- [x] Best Time page inspected in browser.
- [x] Birth Reading page inspected in browser.
- [x] Trust/methodology/policy pages inspected in browser.
- [x] Public infrastructure/developer story inspected and improved.

## Runtime States

- [x] API timeout/network messages mention public demo wake-up and retry.
- [x] Retry/loading behavior inspected in browser.
- [x] No page shows unexplained `Pending` forever.

## Verification

- [x] `npm --prefix frontend run build` passed.
- [x] Old Cloud Run grep passed for frontend and `.env.example`.
- [x] Prohibited frontend phrase grep passed.
- [x] Browser smoke checks completed.
- [x] Final audit completed.

## Push Status

- [x] First priority fix committed locally.
- [x] Second UI hardening loop committed locally.
- [ ] Remote push complete. Blocked because GitHub credentials are invalid.

## Deployment Notes

Cloudflare Pages:
- `VITE_API_BASE=https://api.prabinghimire1.com.np/v3/api`

Render backend:
- `PARVA_ENABLE_EXPERIMENTAL_API=false`
- `PARVA_ENV=public`
- `PARVA_SOURCE_URL=https://github.com/dantwoashim/Project_Parva`
- `CORS_ALLOW_ORIGINS=https://prabinghimire1.com.np,https://www.prabinghimire1.com.np,https://project-parva.pages.dev`
