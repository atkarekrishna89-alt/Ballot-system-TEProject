"""Service layer for Vote business logic — enforces anonymity and prevents duplicates."""

from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import generate_vote_token, hash_vote_token
from app.repositories.vote_repository import VoteRepository
from app.repositories.election_repository import (
    ElectionRepository,
    CandidateRepository,
    # VoterRepository is no longer needed for eligibility checks
)


class VoteService:
    """Business logic for voting — 3-level duplicate prevention + anonymity."""

    @staticmethod
    def cast_vote(db: Session, user_id: str, election_id: str, candidate_id: str):
        """
        Cast a vote with full validation:
        1. Election must exist and be ACTIVE
        2. Time window check (start_time <= now <= end_time)
        3. Voter must be eligible
        4. Candidate must belong to election
        5. Duplicate vote check via hashed token
        6. Store anonymous vote
        """

        # 1. Election exists?
        election = ElectionRepository.get_by_id(db, election_id)
        if not election:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Election not found",
            )

        # 2. Election status check
        if election.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Election is not active (current status: {election.status})",
            )

        # 3. Time window check
        now = datetime.now(timezone.utc)
        if now < election.start_time.replace(tzinfo=timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Election has not started yet",
            )
        if now > election.end_time.replace(tzinfo=timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Election has ended",
            )

        # 4. Voter eligibility is implicit; all registered users may vote.  No per-
        # election check required.
        # 5. Candidate belongs to election?
        candidate = CandidateRepository.get_by_id(db, candidate_id)
        if not candidate or candidate.election_id != election_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid candidate for this election",
            )

        # 6. Determine identifier for anonymous token. If user has an employee ID
        # (our "meaningful id"/AI identifier), use it instead of UUID so that the
        # same person cannot vote twice even if they created multiple accounts.
        user = None
        from app.repositories.user_repository import UserRepository
        user = UserRepository.get_by_id(db, user_id)
        identifier = user.emp_id if user and user.emp_id else user_id

        # 7. Generate anonymous vote token
        vote_token = generate_vote_token(identifier, election_id)
        hashed_token = hash_vote_token(vote_token)

        # 7. Duplicate check (backend validation)
        if VoteRepository.check_duplicate(db, election_id, hashed_token):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already voted in this election",
            )

        # 8. Cast the anonymous vote
        vote = VoteRepository.cast_vote(db, election_id, candidate_id, hashed_token)

        return {
            "message": "Vote cast successfully",
            "election_id": election_id,
            "voted_at": vote.created_at,
        }

    @staticmethod
    def get_results(db: Session, election_id: str):
        """Get election results — only available for closed elections."""
        election = ElectionRepository.get_by_id(db, election_id)
        if not election:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Election not found",
            )

        if election.status != "closed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Results are only available after the election is closed",
            )

        results = VoteRepository.get_results(db, election_id)
        total_votes = VoteRepository.get_total_votes(db, election_id)

        return {
            "election_id": election_id,
            "title": election.title,
            "status": election.status,
            "total_votes": total_votes,
            "results": [
                {
                    "candidate_id": r[0],
                    "candidate_name": r[1],
                    "vote_count": r[2],
                }
                for r in results
            ],
        }

    @staticmethod
    def check_vote_status(db: Session, user_id: str, election_id: str):
        """Check if a user has already voted in an election."""
        # use same identifier logic as cast_vote
        from app.repositories.user_repository import UserRepository
        user = UserRepository.get_by_id(db, user_id)
        identifier = user.emp_id if user and user.emp_id else user_id
        vote_token = generate_vote_token(identifier, election_id)
        hashed_token = hash_vote_token(vote_token)
        has_voted = VoteRepository.check_duplicate(db, election_id, hashed_token)
        return {"election_id": election_id, "has_voted": has_voted}
