# Project Parva (v3 Public Profile)

Project Parva is an ephemeris-backed Nepali temporal engine and festival platform.
It focuses on one core question: **"What is the correct date?"**

## What is implemented
1. BS conversion + tithi + panchanga + sankranti + adhik handling.
2. Festival APIs and explainability traces.
3. Public API profile: `/v3/api/*` (with `/api/*` alias).
4. Personal stack:
   - Personal Panchanga
   - Muhurta
   - Kundali
5. React frontend with Explorer, Detail, Panchanga, iCal, Personal, Muhurta, Kundali, and Dashboard routes.

See `/Users/rohanbasnet14/Documents/Project_Parva/docs/AS_BUILT.md` for evidence-only status.

## Quick start

### Backend
```bash
cd /Users/rohanbasnet14/Documents/Project_Parva
PYTHONPATH=backend uvicorn app.main:app --app-dir backend --reload --port 8000
```

### Frontend
```bash
cd /Users/rohanbasnet14/Documents/Project_Parva/frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`  
API: `http://localhost:8000/v3/api`

## Public API examples
```bash
# calendar conversion
curl 'http://localhost:8000/v3/api/calendar/convert?date=2026-02-15'

# personal panchanga
curl 'http://localhost:8000/v3/api/personal/panchanga?date=2026-02-15&lat=27.7172&lon=85.3240&tz=Asia/Kathmandu'

# muhurta windows
curl 'http://localhost:8000/v3/api/muhurta/auspicious?date=2026-02-15&type=vivah'

# kundali
curl 'http://localhost:8000/v3/api/kundali?datetime=2026-02-15T06:30:00%2B05:45&lat=27.7172&lon=85.3240&tz=Asia/Kathmandu'

```

## Validation commands
```bash
cd /Users/rohanbasnet14/Documents/Project_Parva
./scripts/release/run_month9_release_gates.sh
```

## Documentation
- `/Users/rohanbasnet14/Documents/Project_Parva/docs/API_REFERENCE_V3.md`
- `/Users/rohanbasnet14/Documents/Project_Parva/docs/PROJECT_BIBLE.md`
- `/Users/rohanbasnet14/Documents/Project_Parva/docs/UI_TEMPORAL_CARTOGRAPHY_SPEC.md`
- `/Users/rohanbasnet14/Documents/Project_Parva/docs/EVALUATOR_GUIDE.md`
- `/Users/rohanbasnet14/Documents/Project_Parva/docs/ENGINE_ARCHITECTURE.md`
- `/Users/rohanbasnet14/Documents/Project_Parva/docs/ACCURACY_METHOD.md`
- `/Users/rohanbasnet14/Documents/Project_Parva/docs/KNOWN_LIMITS.md`
- `/Users/rohanbasnet14/Documents/Project_Parva/docs/spec/PARVA_TEMPORAL_SPEC_V1.md`
- `/Users/rohanbasnet14/Documents/Project_Parva/docs/public_beta/month9_release_dossier.md`

## Experimental tracks
`/v2`, `/v4`, `/v5` are disabled by default and only enabled with:
```bash
PARVA_ENABLE_EXPERIMENTAL_API=true
```
