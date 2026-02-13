# PROJECT PARVA — Known Issues & Pitfalls

> **Purpose**: Document known issues, potential pitfalls, and how to avoid/fix them. Read when things go wrong.

---

## Context & Session Issues

### Issue: LLM Writes Minimal/Half-Ass Code
**Symptom**: Functions without docstrings, missing error handling, no tests
**Prevention**: 
1. Read PROJECT_BIBLE.md Section II (Quality Standards) before coding
2. Explicitly remind: "Follow full specifications, not minimal implementation"
3. Check each function against the checklist:
   - Does it have a docstring?
   - Does it have type hints?
   - Does it have error handling?
   - Does it have tests?

**Recovery**: Review code against quality checklist, fix deficiencies

---

### Issue: LLM Tries to Complete Too Fast
**Symptom**: Skipping steps, incomplete implementations, moving to next task prematurely
**Prevention**:
1. Follow ROADMAP.md hour-by-hour during build phase
2. Don't mark task complete until verified
3. Run tests before moving to next task

**Recovery**: Slow down, go back to incomplete step, finish properly

---

### Issue: LLM Loses Context Mid-Implementation
**Symptom**: Asking about things already decided, redoing work, inconsistent implementations
**Prevention**:
1. Start each session with `/parva-start` or `/parva-recover`
2. Read CHANGELOG.md before starting
3. Check TASK.md for in-progress items

**Recovery**: Run recovery workflow, read relevant docs, ask user for clarification

---

### Issue: Account Switch Mid-Task
**Symptom**: New session with no memory of previous work
**Prevention**: 
1. End sessions intentionally with `/parva-end`
2. Commit frequently
3. Update CHANGELOG.md before switching

**Recovery**:
1. Run `/parva-recover`
2. Read last CHANGELOG entry
3. Ask user: "What was the last thing completed?"
4. Resume from checkpoint

---

### Issue: Conflicting Implementations
**Symptom**: Different approaches in different files, inconsistent data formats
**Prevention**:
1. Read DECISIONS_LOG.md for established patterns
2. Follow existing code patterns
3. Check PROJECT_BIBLE.md for specifications

**Recovery**: Identify the authoritative pattern, refactor inconsistent code

---

## Code & Technical Issues

### Issue: Bikram Sambat Dates Are Wrong
**Symptom**: Festival dates don't match known dates
**Cause**: Lookup table error or tithi calculation bug
**Prevention**: 
1. Verify BS_CALENDAR_DATA against official sources
2. Test every year 2080-2090 at minimum
3. Cross-reference with Nepal government calendar

**Recovery**:
```python
# Debug steps
1. Print the intermediate calculation steps
2. Check the BS year start date
3. Verify month lengths for that year
4. Compare with online converter
```

---

### Issue: Tithi Calculation Off By A Day
**Symptom**: Festival start date is ±1 day from expected
**Cause**: Time zone issues, astronomical approximation error
**Prevention**:
1. Document that ±1 day is acceptable for lunar calculations
2. Use Nepal timezone (UTC+5:45) consistently
3. Consider tithi at noon local time

**Recovery**: Flag in UI as "approximate" or adjust by checking multiple sources

---

### Issue: Temple IDs Don't Match
**Symptom**: Map shows wrong location or "location not found"
**Cause**: Festival data references non-existent OSM IDs
**Prevention**:
1. Run validation script to check all IDs exist
2. Use facility IDs exactly as they appear in facilities.geojson

**Recovery**:
```bash
# Find valid temple IDs
grep -o '"facility_id": "[^"]*"' data/processed/facilities.geojson | head -20
```

---

### Issue: Frontend API Calls Fail
**Symptom**: Loading states forever, empty data, console errors
**Cause**: Backend not running, wrong endpoint, CORS issues
**Prevention**:
1. Start backend before testing frontend
2. Check endpoint URLs match routes.py
3. Verify CORS is configured

**Recovery**:
```bash
# Check backend is running
curl http://localhost:8000/api/festivals

# Check console for specific error
# Open browser dev tools → Network tab
```

---

### Issue: Animations Are Janky
**Symptom**: Choppy, stuttering, low FPS animations
**Cause**: Layout thrashing, expensive repaints, too many animations
**Prevention**:
1. Use transform and opacity only (GPU accelerated)
2. Add will-change for animated elements
3. Test in production build, not dev mode

**Recovery**:
- Use Chrome DevTools Performance tab to identify slow frames
- Simplify animation or reduce number of animated elements

---

## Content Issues

### Issue: Mythology Content Is Inaccurate
**Symptom**: Incorrect stories, wrong deity associations, factual errors
**Prevention**:
1. Cross-reference multiple sources
2. Mark uncertain claims as "according to legend"
3. Prefer Nepali sources over generic Hindu mythology sites
4. Have someone knowledgeable review

**Recovery**: Research and correct, add source citations

---

### Issue: Ritual Times Are Wrong
**Symptom**: Events documented at wrong times of day
**Prevention**:
1. Research actual festival observations
2. Check Nepali news coverage of recent festivals
3. Use approximate times if exact unknown

**Recovery**: Flag as "approximate timing" or research more

---

### Issue: Content Feels Like Wikipedia
**Symptom**: Dry, encyclopedic, list of facts
**Prevention**:
1. Follow Writing Style Guide in PROJECT_BIBLE.md
2. Write as narrative, not encyclopedia
3. Include sensory details
4. Start with story, not dates

**Recovery**: Rewrite in narrative style, read aloud to check flow

---

## Build & Deploy Issues

### Issue: npm install Fails
**Symptom**: Node module installation errors
**Recovery**:
```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

---

### Issue: Python Imports Fail
**Symptom**: ModuleNotFoundError
**Recovery**:
```bash
cd backend
pip install -r requirements.txt
# Make sure you're in virtual environment if using one
```

---

### Issue: Tests Pass Locally But Fail on Verification
**Symptom**: Works on your machine but breaks in demo
**Prevention**:
1. Test on presentation machine before demo
2. Don't rely on local environment variables
3. Commit .env.example with required vars

**Recovery**: Debug on target machine, check environment differences

---

## Demo Issues

### Issue: Demo Crashes Mid-Presentation
**Symptom**: Application error during thesis demo
**Prevention**:
1. Have backup video recording
2. Pre-cache all data (run through demo beforehand)
3. Disable features that might fail
4. Have fallback slides with screenshots

**Recovery**: Switch to backup video or screenshots

---

### Issue: Slow Loading During Demo
**Symptom**: Long loading times, awkward pauses
**Prevention**:
1. Run dev server in production mode
2. Pre-load all data before demo
3. Use local assets, not external APIs
4. Cache aggressively

**Recovery**: Narrate while waiting, "As the data loads..."

---

## Recovery Commands Cheat Sheet

```bash
# Check what exists
ls -la backend/app/calendar/ backend/app/festivals/ frontend/src/components/Festival/

# Quick backend test
cd backend && python -c "from app.main import app; print('OK')"

# Quick frontend test
cd frontend && npm run build

# Run all tests
pytest tests/ -v --tb=short

# Find a specific festival in data
grep -A10 '"id": "dashain"' data/festivals/festivals.json

# Check git status
git status
git log --oneline -10

# Stash changes if switching context
git stash push -m "WIP: [description]"
git stash pop
```

---

> **Remember**: When in doubt, read PROJECT_BIBLE.md. When stuck, run `/parva-recover`. When starting fresh, run `/parva-start`.
