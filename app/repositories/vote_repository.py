"""Repository layer for Vote database operations."""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.vote import Vote
from app.models.election import Candidate


class VoteRepository:
    """Data access for Vote operations — maintains anonymity."""

    @staticmethod
    def cast_vote(
        db: Session,
        election_id: str,
        candidate_id: str,
        hashed_voter_token: str,
    ) -> Vote:
        vote = Vote(
            election_id=election_id,
            candidate_id=candidate_id,
            hashed_voter_token=hashed_voter_token,
        )
        db.add(vote)
        db.commit()
        db.refresh(vote)
        return vote

    @staticmethod
    def check_duplicate(db: Session, election_id: str, hashed_voter_token: str) -> bool:
        """Check if a vote with this token already exists for this election."""
        existing = (
            db.query(Vote)
            .filter(
                Vote.election_id == election_id,
                Vote.hashed_voter_token == hashed_voter_token,
            )
            .first()
        )
        return existing is not None

    @staticmethod
    def get_results(db: Session, election_id: str) -> List[Tuple[str, str, int]]:
        """Get vote counts per candidate for an election."""
        results = (
            db.query(
                Candidate.id,
                Candidate.name,
                func.count(Vote.id).label("vote_count"),
            )
            .outerjoin(Vote, Vote.candidate_id == Candidate.id)
            .filter(Candidate.election_id == election_id)
            .group_by(Candidate.id, Candidate.name)
            .order_by(func.count(Vote.id).desc())
            .all()
        )
        return results

    @staticmethod
    def get_total_votes(db: Session, election_id: str) -> int:
        return db.query(func.count(Vote.id)).filter(Vote.election_id == election_id).scalar() or 0
