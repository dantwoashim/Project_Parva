# Sources Layer

`backend/app/sources/` owns data loading and source precedence.

Responsibilities:
- Load rules and overrides from JSON.
- Load official ground truth snapshots.
- Expose source-priority policy for conflict resolution.

This layer intentionally keeps I/O out of the engine.
