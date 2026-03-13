"""
Locations Module
================

Temple and sacred location management.
"""

from .models import (
    Coordinates as Coordinates,
)
from .models import (
    FestivalLocationMapping as FestivalLocationMapping,
)
from .models import (
    Temple as Temple,
)
from .models import (
    TempleSummary as TempleSummary,
)
from .repository import (
    get_all_temples as get_all_temples,
)
from .repository import (
    get_temple_by_id as get_temple_by_id,
)
from .repository import (
    get_temple_summaries as get_temple_summaries,
)
from .repository import (
    get_temples_by_festival as get_temples_by_festival,
)
from .routes import router as router

__all__ = [
    "Coordinates",
    "FestivalLocationMapping",
    "Temple",
    "TempleSummary",
    "get_all_temples",
    "get_temple_by_id",
    "get_temple_summaries",
    "get_temples_by_festival",
    "router",
]
