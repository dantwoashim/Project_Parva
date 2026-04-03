# Frontier Roadmap

Project Parva becomes genuinely unusual when it stops being only a calendar API and becomes a temporal authority system for Nepal and the Nepali diaspora.

## What Makes It Different

- It should answer not only "what is the date?" but also "according to which authority, for which tradition, and with what evidence?"
- It should preserve disagreement instead of flattening it.
- It should expose machine-readable provenance, uncertainty, and cultural profile selection as first-class product features.

## Near-Term Moves

1. Multi-authority resolution
   Parva should let clients request canonical, government-listing, estimated, or tradition-specific answers explicitly. This is the beginning of that work.

2. Replayable historical snapshots
   Every returned result should be reproducible against a frozen dataset/rules snapshot so that citations and institutional use are trustworthy.

3. Festival disagreement atlas
   Build a visual and API layer that shows where official, computed, and community calendars disagree by day and by tradition.

4. Institutional integration surfaces
   Ship SDKs, widgets, ICS feeds, embed blocks, and school/media/temple presets so the project spreads through infrastructure rather than only through an app.

## World-Class Direction

1. Cultural time graph
   Model festivals, tithi, lunar months, solar ingress points, places, rituals, and profiles as a linked temporal graph instead of isolated endpoints.

2. Authority negotiation engine
   Let clients specify a policy like "prefer MoHA, then Rashtriya Panchang, then computed ephemeris" and receive a deterministic answer with fallback reasoning.

3. Auditable calendar intelligence
   Add signed snapshots, public verification pages, and diff views between yearly releases so institutions can defend why a date changed.

4. Living Nepali time standard
   Turn Parva into a de facto reference layer for BS/AD conversion, panchanga, festivals, and regional observance variants across products.

## Next Concrete Builds

- Expose authority-aware festival resolution in more public endpoints.
- Add conflict-aware OpenAPI examples and SDK helpers.
- Build a "why these two calendars disagree" API and UI.
- Add yearly reviewed releases with changelogs and signed provenance.
