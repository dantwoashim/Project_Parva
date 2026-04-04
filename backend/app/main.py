"""Project Parva application entrypoint.

Public API profile is v3-first:
- /v3/api/* (primary)
- /api/* (compat alias)

Experimental tracks (/v2, /v4, /v5) are disabled unless
PARVA_ENABLE_EXPERIMENTAL_API=true.
"""

from app.bootstrap import create_app

app = create_app()
