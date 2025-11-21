"""
Database Schemas for Lümn Note

Each Pydantic model maps to a MongoDB collection using the lowercase class name.
Use these models for validation when creating or updating documents.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Journal(BaseModel):
    title: str = Field(..., description="Journal title")
    cover_style: str = Field("pastel-pink", description="Cover style identifier")
    paper_style: str = Field("dotted", description="Page paper style: dotted, lined, grid, blank")
    owner: Optional[str] = Field(None, description="Owner identifier if authentication is added later")

class JournalPage(BaseModel):
    journal_id: str = Field(..., description="Related journal id")
    date: str = Field(..., description="ISO date string YYYY-MM-DD for daily pages")
    content: str = Field("", description="Rich text or markdown content")
    font: str = Field("Inter", description="Font family name")
    font_size: int = Field(16, ge=8, le=64)
    color: str = Field("#1f2937")
    alignment: str = Field("left", description="left|center|right|justify")
    background: Optional[str] = Field(None, description="Optional background style identifier")

class CalendarEvent(BaseModel):
    date: str = Field(..., description="ISO date YYYY-MM-DD")
    title: str = Field(..., description="Short title for the calendar cell")
    highlight: Optional[str] = Field(None, description="Highlight color token")
    emoji: Optional[str] = Field(None, description="Optional emoji shortcut")

class Sticker(BaseModel):
    date: str = Field(..., description="ISO date YYYY-MM-DD the sticker belongs to")
    category: str = Field("decor", description="Category: emotions|nature|decor|work|custom")
    label: str = Field(..., description="Sticker label or emoji")
    x: float = Field(0, description="x position in cell (0-1)")
    y: float = Field(0, description="y position in cell (0-1)")
    size: float = Field(1.0, description="relative size multiplier")

# Optional: Drawing strokes for pressure/tilt future expansion
class StrokePoint(BaseModel):
    x: float
    y: float
    p: Optional[float] = Field(None, description="pressure 0-1")
    t: Optional[float] = Field(None, description="timestamp")

class Drawing(BaseModel):
    date: str = Field(..., description="ISO date YYYY-MM-DD")
    tool: str = Field("pen", description="pen|brush|marker")
    color: str = Field("#111827")
    size: float = Field(2.0)
    points: List[StrokePoint] = Field(default_factory=list)
