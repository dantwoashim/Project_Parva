# Private Migration Candidates

These items are not removed automatically here because they may still matter for provenance or future migration, but they are poor fits for a permanent public repo.

| Path | Why it is a candidate | Current usage | Recommendation |
| --- | --- | --- | --- |
| `data/source_archive/secondary/` | Raw third-party HTML snapshots include copied markup and embedded page-level tokens from source sites | Not used by the runtime path | Move to a private evidence bucket or scrub before future public promotion |
| `data/source_archive/ratopati/event_days_2000_2100.json` | Provider-derived bulk archive may need redistribution review | Referenced by archive/source tooling, not the core API path | Review licensing and keep only a public-safe derivative if needed |
| Future admin-only runbooks or credentials | Not part of the OSS guarantee | None should be committed here | Keep operational material outside the public repo |

The presence of a path here does not mean it is secret. It means the public repository is probably not the best long-term home for it.
