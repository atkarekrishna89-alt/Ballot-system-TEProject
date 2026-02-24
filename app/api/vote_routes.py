"""Vote API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.vote_schema import VoteCast, VoteConfirmation, ElectionResults, VoteStatusResponse
from app.services.vote_service import VoteService

router = APIRouter(prefix="/api/vote", tags=["Voting"])


@router.post("/", response_model=VoteConfirmation)
def cast_vote(
    data: VoteCast,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cast a vote in an election. Enforces anonymity and prevents duplicates."""
    return VoteService.cast_vote(
        db,
        user_id=current_user.id,
        election_id=data.election_id,
        candidate_id=data.candidate_id,
    )


@router.get("/results/{election_id}", response_model=ElectionResults)
def get_results(
    election_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get election results (only available after election is closed)."""
    return VoteService.get_results(db, election_id)


@router.get("/status/{election_id}", response_model=VoteStatusResponse)
def check_vote_status(
    election_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check if the current user has already voted in an election."""
    return VoteService.check_vote_status(db, current_user.id, election_id)
