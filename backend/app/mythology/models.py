"""
Mythology Data Models
=====================

Pydantic models for deity and mythology content.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class Legend(BaseModel):
    """A single legend or mythological story."""
    
    title: str = Field(..., description="Title of the legend")
    content: str = Field(..., description="The story content")
    source: Optional[str] = Field(None, description="Source reference")
    related_festival: Optional[str] = Field(None, description="Festival this legend explains")


class Deity(BaseModel):
    """A deity in the Nepali pantheon."""
    
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="English name")
    name_nepali: str = Field(..., description="Nepali name")
    name_sanskrit: Optional[str] = Field(None, description="Sanskrit name")
    
    role: str = Field(..., description="Role/domain description")
    domain: List[str] = Field(default_factory=list, description="Domains of influence")
    
    iconography: Optional[str] = Field(None, description="How to identify in art")
    vahana: Optional[str] = Field(None, description="Divine vehicle/mount")
    consort: Optional[str] = Field(None, description="Consort deity")
    
    mythology: str = Field(..., description="Mythological background")
    nepali_significance: Optional[str] = Field(None, description="Specific importance in Nepal")
    
    associated_festivals: List[str] = Field(default_factory=list, description="Festival IDs")
    associated_temples: List[str] = Field(default_factory=list, description="Temple/facility IDs")
    
    class Config:
        frozen = True


class DeitySummary(BaseModel):
    """Lightweight deity summary for list views."""
    
    id: str
    name: str
    name_nepali: str
    role: str
    associated_festivals: List[str] = Field(default_factory=list)
