"""Pydantic schemas for Organization operations."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str
    description: Optional[str] = None


class OrganizationResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True
