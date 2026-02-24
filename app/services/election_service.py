"""Service layer for Election business logic."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.election_repository import (
    ElectionRepository,
    CandidateRepository,
    VoterRepository,
)
from app.repositories.organization_repository import OrganizationRepository


class ElectionService:
    """Business logic for Election, Candidate, and Voter operations."""

    # --- Elections ---
    @staticmethod
    def create_election(db: Session, organization_id: str, title: str, description: str,
                        start_time, end_time, created_by: str):
        org = OrganizationRepository.get_by_id(db, organization_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        if end_time <= start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after start time",
            )
        return ElectionRepository.create(
            db,
            organization_id=organization_id,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            created_by=created_by,
        )

    @staticmethod
    def get_election(db: Session, election_id: str):
        election = ElectionRepository.get_by_id(db, election_id)
        if not election:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Election not found",
            )
        return election

    @staticmethod
    def get_all_elections(db: Session, skip: int = 0, limit: int = 100):
        return ElectionRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def get_elections_by_org(db: Session, org_id: str):
        return ElectionRepository.get_by_organization(db, org_id)

    @staticmethod
    def update_election(db: Session, election_id: str, **kwargs):
        election = ElectionRepository.get_by_id(db, election_id)
        if not election:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Election not found",
            )
        if election.status != "draft":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only update elections in draft status",
            )
        return ElectionRepository.update(db, election, **kwargs)

    @staticmethod
    def activate_election(db: Session, election_id: str):
        election = ElectionRepository.get_by_id(db, election_id)
        if not election:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Election not found",
            )
        if election.status != "draft":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only activate elections in draft status",
            )
        candidates = CandidateRepository.get_by_election(db, election_id)
        if len(candidates) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Election must have at least 2 candidates to activate",
            )
        return ElectionRepository.update_status(db, election, "active")

    @staticmethod
    def close_election(db: Session, election_id: str):
        election = ElectionRepository.get_by_id(db, election_id)
        if not election:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Election not found",
            )
        if election.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only close active elections",
            )
        return ElectionRepository.update_status(db, election, "closed")

    @staticmethod
    def delete_election(db: Session, election_id: str):
        election = ElectionRepository.get_by_id(db, election_id)
        if not election:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Election not found",
            )
        # only closed elections may be removed; drafts should be edited instead
        if election.status != "closed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only closed elections can be deleted",
            )
        ElectionRepository.delete(db, election)
        return {"message": "Election deleted"}

    # --- Candidates ---
    @staticmethod
    def add_candidate(db: Session, election_id: str, name: str, description: str = None):
        election = ElectionRepository.get_by_id(db, election_id)
        if not election:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Election not found",
            )
        if election.status != "draft":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only add candidates to draft elections",
            )
        return CandidateRepository.create(db, election_id=election_id, name=name, description=description)

    @staticmethod
    def get_candidates(db: Session, election_id: str):
        return CandidateRepository.get_by_election(db, election_id)

    @staticmethod
    def delete_candidate(db: Session, candidate_id: str):
        candidate = CandidateRepository.get_by_id(db, candidate_id)
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found",
            )
        election = ElectionRepository.get_by_id(db, candidate.election_id)
        if election and election.status != "draft":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only remove candidates from draft elections",
            )
        CandidateRepository.delete(db, candidate)
        return {"message": "Candidate removed"}

    # --- Voters ---
    @staticmethod
    def add_voter(db: Session, user_id: str, election_id: str):
        # user_id may actually be an employee ID; resolve to actual user UUID
        election = ElectionRepository.get_by_id(db, election_id)
        if not election:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Election not found",
            )
        # try to fetch by id first
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            # attempt lookup by emp_id
            user = UserRepository.get_by_emp_id(db, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
        actual_id = user.id
        existing = VoterRepository.get_voter(db, actual_id, election_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already registered as a voter for this election",
            )
        return VoterRepository.add_voter(db, user_id=actual_id, election_id=election_id)

    @staticmethod
    def get_voters(db: Session, election_id: str):
        return VoterRepository.get_voters_for_election(db, election_id)

    @staticmethod
    def remove_voter(db: Session, user_id: str, election_id: str):
        voter = VoterRepository.get_voter(db, user_id, election_id)
        if not voter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voter not found",
            )
        VoterRepository.remove_voter(db, voter)
        return {"message": "Voter removed"}
