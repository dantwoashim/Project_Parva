# As-Built (Current)

This file describes only what is implemented and verifiable in the repository now.

## Implemented
1. Ephemeris-backed calendar engine (BS conversion, tithi, panchanga, sankranti, adhik handling).
2. Public v3 API profile (`/v3/api/*`) with `/api/*` convenience alias.
3. Experimental tracks (`/v2`, `/v4`, `/v5`) behind `PARVA_ENABLE_EXPERIMENTAL_API`.
4. Festival explorer, detail, panchanga viewer, iCal feed UI.
5. Personal stack APIs and UI pages:
   - Personal Panchanga
   - Muhurta
   - Kundali
6. Deterministic trace generation + provenance metadata on key responses.
7. CI pipeline for backend tests, frontend build, contract freeze check, conformance run.

## Not implemented (or partial)
1. 300+ fully computed festival rules with verified regional jurisprudence.
2. Full institutional governance/operations model beyond repository artifacts.
3. Persistent community layer and AR/WebXR production features.

## Evidence pointers
- API bootstrap: `backend/app/bootstrap/`
- Personal endpoints: `backend/app/api/personal_routes.py`,
  `backend/app/api/muhurta_routes.py`, `backend/app/api/kundali_routes.py`
- Frontend routes/pages: `frontend/src/App.jsx`
- Conformance report output: generated artifact `reports/conformance_report.json`
  (see `docs/GENERATED_ARTIFACTS.md`)
