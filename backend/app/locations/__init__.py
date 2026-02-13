"""
Locations Module
================

Temple and sacred location management.
"""

from .models import Temple, TempleSummary, Coordinates, FestivalLocationMapping
from .repository import (
    get_all_temples,
    get_temple_by_id,
    get_temples_by_festival,
    get_temple_summaries,
)
from .routes import router
