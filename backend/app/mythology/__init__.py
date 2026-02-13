"""
Mythology Module
================

Deity and mythology data management for Project Parva.
Provides access to Nepal's rich mythological content including
deities, legends, and their connections to festivals.
"""

from .models import Deity, Legend, DeitySummary
from .repository import get_deity, get_all_deities, get_deity_festivals

__all__ = [
    "Deity",
    "Legend",
    "DeitySummary",
    "get_deity",
    "get_all_deities",
    "get_deity_festivals",
]
