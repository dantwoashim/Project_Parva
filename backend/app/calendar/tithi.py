"""Shadowed compatibility stub for the canonical tithi package.

Python resolves ``app.calendar.tithi`` to the sibling package directory, not
this file. The public runtime source of truth is ``backend/app/calendar/tithi/``.
This file is retained only so repo path references and direct file inspections
do not find an old competing implementation.
"""

from app.calendar.tithi import *  # noqa: F401,F403
