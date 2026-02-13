# 🚨 SESSION RECOVERY — READ THIS FIRST 🚨

> **When to read this**: At the START of every new chat session, after account switches, or whenever you (the LLM) seem confused about the project.

---

## WHO YOU ARE

You are helping **Rohan Basnet** (BSc CSIT final year student in Nepal) build **Project Parva** — a premium festival discovery system for Nepal. You are a powerful coding LLM that can implement full features quickly but tends to lose context and sometimes write "half-ass" code unless reminded of quality standards.

---

## IMMEDIATE CONTEXT RECOVERY

### Step 1: Check Current State (Run These Commands)

```bash
# What day are we on?
cat "/Users/rohanbasnet14/Documents/Nepal as a System/Project Parva/TASK.md" | head -20

# What was last done?
cat "/Users/rohanbasnet14/Documents/Nepal as a System/Project Parva/CHANGELOG.md" | tail -30

# Any open decisions?
cat "/Users/rohanbasnet14/Documents/Nepal as a System/Project Parva/DECISIONS_LOG.md" | tail -20
```

### Step 2: Read Core Files (In This Order)

1. **TASK.md** — See what's checked off and what's in progress `[/]`
2. **CHANGELOG.md** — See what was done in the last session
3. **PROJECT_BIBLE.md Section II** — Re-read quality standards before any coding
4. **ROADMAP.md** — Find the current day and see detailed tasks

### Step 3: Verify Current State

```bash
# Check if backend runs
cd "/Users/rohanbasnet14/Documents/Nepal as a System" && cd backend && python -c "from app.main import app; print('Backend OK')"

# Check if frontend runs  
cd "/Users/rohanbasnet14/Documents/Nepal as a System" && cd frontend && npm run build 2>&1 | tail -5

# Run tests to see what's working
cd "/Users/rohanbasnet14/Documents/Nepal as a System" && pytest tests/ -v --tb=no -q 2>&1 | tail -20
```

---

## CRITICAL REMINDERS

### Quality Standards (Memorize These)
```
□ Every function has a docstring
□ Type hints on all Python functions
□ PropTypes on all React components  
□ No magic numbers — constants are named
□ Error handling for every API call
□ Loading/error/empty states for every component
□ Animations use easing (never linear)
□ Transitions are 300-600ms
```

### My Weaknesses (Combat These)
```
⚠️ I try to complete things too fast → SLOW DOWN, read specs
⚠️ I write minimal code unless pushed → Follow FULL specifications
⚠️ I lose context mid-implementation → Check TASK.md frequently
⚠️ I might redo work → Check CHANGELOG.md before starting
⚠️ I forget design decisions → Check DECISIONS_LOG.md
```

---

## FILE LOCATIONS

```
/Users/rohanbasnet14/Documents/Nepal as a System/
├── Project Parva/
│   ├── PROJECT_BIBLE.md      ← The law. Read before coding.
│   ├── ROADMAP.md            ← Day-by-day tasks with details
│   ├── TASK.md               ← Current progress checkboxes
│   ├── CHANGELOG.md          ← What was done when
│   ├── DECISIONS_LOG.md      ← Why choices were made
│   └── SESSION_RECOVERY.md   ← THIS FILE
│
├── backend/
│   ├── app/
│   │   ├── calendar/         ← Calendar engine (if built)
│   │   ├── festivals/        ← Festival API (if built)
│   │   └── main.py           ← Main FastAPI app
│   └── data/
│       └── festivals/        ← Festival JSON data
│
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Festival/     ← Festival components (if built)
│       │   └── Calendar/     ← Calendar components (if built)
│       └── pages/
│           └── ParvaPage.jsx ← Main page (if built)
│
└── data/
    └── processed/
        └── facilities.geojson ← OSM temple data (existing)
```

---

## SESSION HANDOFF PROTOCOL

### When Ending a Session

Before the session ends, I MUST:

1. **Update TASK.md** — Check off completed items, mark in-progress items with `[/]`
2. **Update CHANGELOG.md** — Log what was done with timestamps
3. **Update DECISIONS_LOG.md** — Log any non-obvious choices made
4. **Commit to git** — `git add . && git commit -m "session: [summary]"`
5. **Note any blockers** — Add to TASK.md Notes section

### When Starting a Session

1. **Read SESSION_RECOVERY.md** (this file)
2. **Run verification commands** (see above)
3. **Read last 3 CHANGELOG entries**
4. **Continue from TASK.md in-progress items**

---

## COMMON RECOVERY SCENARIOS

### Scenario: "I don't know what day we're on"
```bash
cat "/Users/rohanbasnet14/Documents/Nepal as a System/Project Parva/TASK.md" | grep -E "^## Day|^\- \[x\]|^\- \[/\]|^\- \[ \]" | head -30
```

### Scenario: "I don't remember what was built"
```bash
# Check if calendar engine exists
ls -la "/Users/rohanbasnet14/Documents/Nepal as a System/backend/app/calendar/" 2>/dev/null || echo "Calendar engine not built yet"

# Check if festival API exists
ls -la "/Users/rohanbasnet14/Documents/Nepal as a System/backend/app/festivals/" 2>/dev/null || echo "Festival API not built yet"

# Check if frontend components exist
ls -la "/Users/rohanbasnet14/Documents/Nepal as a System/frontend/src/components/Festival/" 2>/dev/null || echo "Festival components not built yet"
```

### Scenario: "I don't know why something was done this way"
```bash
cat "/Users/rohanbasnet14/Documents/Nepal as a System/Project Parva/DECISIONS_LOG.md"
```

### Scenario: "Tests are failing and I don't know why"
```bash
# Show failing tests with details
cd "/Users/rohanbasnet14/Documents/Nepal as a System" && pytest tests/ -v --tb=short 2>&1 | grep -A5 "FAILED"
```

### Scenario: "User switched accounts mid-task"
1. Ask user: "What was the last thing completed?"
2. Read CHANGELOG.md for context
3. Run verification commands
4. Resume from last incomplete task

---

## SLASH COMMAND

You can trigger this recovery by asking the user to say:
```
/parva-recover
```

This should prompt reading SESSION_RECOVERY.md and running diagnostics.

---

## EMERGENCY CONTACTS

If completely stuck:
1. Re-read PROJECT_BIBLE.md entirely
2. Re-read ROADMAP.md for current day
3. Ask user for clarification on current state
4. Start with smallest verifiable task

---

> **Remember**: Slow is smooth, smooth is fast. Read the docs before coding. Check the specs before implementing. Quality over speed.
