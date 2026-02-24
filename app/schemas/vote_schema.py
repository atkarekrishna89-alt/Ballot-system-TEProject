"""Pydantic schemas for Vote operations."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class VoteCast(BaseModel):
    election_id: str
    candidate_id: str


class VoteConfirmation(BaseModel):
    message: str
    election_id: str
    voted_at: datetime


class CandidateResult(BaseModel):
    candidate_id: str
    candidate_name: str
    vote_count: int


class ElectionResults(BaseModel):
    election_id: str
    title: str
    status: str
    total_votes: int
    results: List[CandidateResult]


class VoteStatusResponse(BaseModel):
    election_id: str
    has_voted: bool
