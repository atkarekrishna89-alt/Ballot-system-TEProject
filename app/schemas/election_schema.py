"""Pydantic schemas for Election, Candidate, and Voter operations."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# --- Election ---
class ElectionCreate(BaseModel):
    organization_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime


class ElectionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ElectionResponse(BaseModel):
    id: str
    organization_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: str
    created_by: str
    created_at: datetime
    candidates: List["CandidateResponse"] = []
    total_votes: Optional[int] = 0

    class Config:
        from_attributes = True


# --- Candidate ---
class CandidateCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CandidateResponse(BaseModel):
    id: str
    election_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- Voter ---
class VoterAdd(BaseModel):
    identifier: str  # can be user UUID or employee ID


class VoterBulkAdd(BaseModel):
    user_ids: List[str]


class VoterResponse(BaseModel):
    id: str
    user_id: str
    election_id: str
    is_eligible: bool
    emp_id: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True
