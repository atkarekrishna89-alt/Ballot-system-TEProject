"""Repository layer for Election, Candidate, and Voter database operations."""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.election import Election, Candidate, Voter


class ElectionRepository:
    """Data access for Election operations."""

    @staticmethod
    def create(db: Session, **kwargs) -> Election:
        election = Election(**kwargs)
        db.add(election)
        db.commit()
        db.refresh(election)
        return election

    @staticmethod
    def get_by_id(db: Session, election_id: str) -> Optional[Election]:
        return db.query(Election).filter(Election.id == election_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Election]:
        return db.query(Election).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_organization(db: Session, org_id: str) -> List[Election]:
        return db.query(Election).filter(Election.organization_id == org_id).all()

    @staticmethod
    def update(db: Session, election: Election, **kwargs) -> Election:
        for key, value in kwargs.items():
            if value is not None and hasattr(election, key):
                setattr(election, key, value)
        db.commit()
        db.refresh(election)
        return election

    @staticmethod
    def update_status(db: Session, election: Election, status: str) -> Election:
        election.status = status
        db.commit()
        db.refresh(election)
        return election

    @staticmethod
    def delete(db: Session, election: Election) -> None:
        db.delete(election)
        db.commit()


class CandidateRepository:
    """Data access for Candidate operations."""

    @staticmethod
    def create(db: Session, election_id: str, name: str, description: Optional[str] = None) -> Candidate:
        candidate = Candidate(election_id=election_id, name=name, description=description)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        return candidate

    @staticmethod
    def get_by_id(db: Session, candidate_id: str) -> Optional[Candidate]:
        return db.query(Candidate).filter(Candidate.id == candidate_id).first()

    @staticmethod
    def get_by_election(db: Session, election_id: str) -> List[Candidate]:
        return db.query(Candidate).filter(Candidate.election_id == election_id).all()

    @staticmethod
    def delete(db: Session, candidate: Candidate) -> None:
        db.delete(candidate)
        db.commit()


class VoterRepository:
    """Data access for Voter operations."""

    @staticmethod
    def add_voter(db: Session, user_id: str, election_id: str) -> Voter:
        voter = Voter(user_id=user_id, election_id=election_id, is_eligible=True)
        db.add(voter)
        db.commit()
        db.refresh(voter)
        return voter

    @staticmethod
    def get_voter(db: Session, user_id: str, election_id: str) -> Optional[Voter]:
        return (
            db.query(Voter)
            .filter(Voter.user_id == user_id, Voter.election_id == election_id)
            .first()
        )

    @staticmethod
    def get_voters_for_election(db: Session, election_id: str) -> List[Voter]:
        return db.query(Voter).filter(Voter.election_id == election_id).all()

    @staticmethod
    def remove_voter(db: Session, voter: Voter) -> None:
        db.delete(voter)
        db.commit()
