"""Election, Candidate, and Voter API routes."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role, get_current_user
from app.models.user import User
from app.schemas.election_schema import (
    ElectionCreate,
    ElectionUpdate,
    ElectionResponse,
    CandidateCreate,
    CandidateResponse,
    # voter schemas retained for compatibility but not used in endpoints
    VoterAdd,
    VoterBulkAdd,
    VoterResponse,
)
from app.services.election_service import ElectionService
from app.repositories.vote_repository import VoteRepository
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/api/elections", tags=["Elections"])


def _election_to_response(e, candidates, db):
    """Build ElectionResponse with total_votes."""
    total_votes = VoteRepository.get_total_votes(db, e.id)
    return ElectionResponse(
        id=e.id, organization_id=e.organization_id, title=e.title,
        description=e.description, start_time=e.start_time, end_time=e.end_time,
        status=e.status, created_by=e.created_by, created_at=e.created_at,
        candidates=[CandidateResponse(
            id=c.id, election_id=c.election_id, name=c.name,
            description=c.description, created_at=c.created_at
        ) for c in candidates],
        total_votes=total_votes,
    )


# --- Election CRUD ---
@router.post("/", response_model=ElectionResponse, status_code=201)
def create_election(
    data: ElectionCreate,
    current_user: User = Depends(require_role("SUPER_ADMIN", "ORG_ADMIN", "ELECTION_MANAGER")),
    db: Session = Depends(get_db),
):
    """Create a new election."""
    election = ElectionService.create_election(
        db,
        organization_id=data.organization_id,
        title=data.title,
        description=data.description,
        start_time=data.start_time,
        end_time=data.end_time,
        created_by=current_user.id,
    )
    candidates = ElectionService.get_candidates(db, election.id)
    return _election_to_response(election, candidates, db)


@router.get("/", response_model=List[ElectionResponse])
def list_elections(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all elections."""
    elections = ElectionService.get_all_elections(db, skip=skip, limit=limit)
    result = []
    for e in elections:
        candidates = ElectionService.get_candidates(db, e.id)
        result.append(_election_to_response(e, candidates, db))
    return result


@router.get("/{election_id}", response_model=ElectionResponse)
def get_election(
    election_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get election by ID."""
    e = ElectionService.get_election(db, election_id)
    candidates = ElectionService.get_candidates(db, e.id)
    return _election_to_response(e, candidates, db)


@router.put("/{election_id}", response_model=ElectionResponse)
def update_election(
    election_id: str,
    data: ElectionUpdate,
    current_user: User = Depends(require_role("SUPER_ADMIN", "ORG_ADMIN", "ELECTION_MANAGER")),
    db: Session = Depends(get_db),
):
    """Update an election (draft only)."""
    update_data = data.model_dump(exclude_unset=True)
    e = ElectionService.update_election(db, election_id, **update_data)
    candidates = ElectionService.get_candidates(db, e.id)
    return _election_to_response(e, candidates, db)


@router.put("/{election_id}/activate")
def activate_election(
    election_id: str,
    current_user: User = Depends(require_role("SUPER_ADMIN", "ORG_ADMIN", "ELECTION_MANAGER")),
    db: Session = Depends(get_db),
):
    """Activate a draft election (must have ≥2 candidates)."""
    election = ElectionService.activate_election(db, election_id)
    return {"message": "Election activated", "status": election.status}


@router.put("/{election_id}/close")
def close_election(
    election_id: str,
    current_user: User = Depends(require_role("SUPER_ADMIN", "ORG_ADMIN", "ELECTION_MANAGER")),
    db: Session = Depends(get_db),
):
    """Close an active election."""
    election = ElectionService.close_election(db, election_id)
    return {"message": "Election closed", "status": election.status}


@router.delete("/{election_id}")
def delete_election(
    election_id: str,
    current_user: User = Depends(require_role("SUPER_ADMIN", "ORG_ADMIN")),
    db: Session = Depends(get_db),
):
    """Delete an election (not if active)."""
    return ElectionService.delete_election(db, election_id)


# --- Candidates ---
@router.post("/{election_id}/candidates", response_model=CandidateResponse, status_code=201)
def add_candidate(
    election_id: str,
    data: CandidateCreate,
    current_user: User = Depends(require_role("SUPER_ADMIN", "ORG_ADMIN", "ELECTION_MANAGER")),
    db: Session = Depends(get_db),
):
    """Add a candidate to an election (draft only)."""
    return ElectionService.add_candidate(db, election_id, data.name, data.description)


@router.get("/{election_id}/candidates", response_model=List[CandidateResponse])
def list_candidates(
    election_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List candidates for an election."""
    return ElectionService.get_candidates(db, election_id)


@router.delete("/candidates/{candidate_id}")
def remove_candidate(
    candidate_id: str,
    current_user: User = Depends(require_role("SUPER_ADMIN", "ORG_ADMIN", "ELECTION_MANAGER")),
    db: Session = Depends(get_db),
):
    """Remove a candidate (draft only)."""
    return ElectionService.delete_candidate(db, candidate_id)


# --- Voters ---
# per-election voter handling has been deprecated – all registered users may vote automatically.
# Endpoints remain for compatibility but are effectively no‑ops or return empty data.

@router.post("/{election_id}/voters", status_code=204)
def add_voter(
    election_id: str,
    data: VoterAdd,
    current_user: User = Depends(require_role("SUPER_ADMIN", "ORG_ADMIN", "ELECTION_MANAGER")),
    db: Session = Depends(get_db),
):
    """No-op: voter registration is global."""
    return None

@router.post("/{election_id}/voters/bulk", status_code=204)
def bulk_add_voters(
    election_id: str,
    data: VoterBulkAdd,
    current_user: User = Depends(require_role("SUPER_ADMIN", "ORG_ADMIN", "ELECTION_MANAGER")),
    db: Session = Depends(get_db),
):
    """No-op bulk add."""
    return None

@router.get("/{election_id}/voters", response_model=List[VoterResponse])
def list_voters(
    election_id: str,
    current_user: User = Depends(require_role("SUPER_ADMIN", "ORG_ADMIN", "ELECTION_MANAGER")),
    db: Session = Depends(get_db),
):
    """Return empty list; voters are not tracked per election."""
    return []

@router.delete("/{election_id}/voters/{user_id}")
def remove_voter(
    election_id: str,
    user_id: str,
    current_user: User = Depends(require_role("SUPER_ADMIN", "ORG_ADMIN", "ELECTION_MANAGER")),
    db: Session = Depends(get_db),
):
    """No-op remove."""
    return None
