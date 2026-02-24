"""Service layer for Organization business logic."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.organization_repository import OrganizationRepository


class OrganizationService:
    """Business logic for Organization operations."""

    @staticmethod
    def create_organization(db: Session, name: str, description: str, created_by: str):
        return OrganizationRepository.create(db, name=name, description=description, created_by=created_by)

    @staticmethod
    def get_organization(db: Session, org_id: str):
        org = OrganizationRepository.get_by_id(db, org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        return org

    @staticmethod
    def get_all_organizations(db: Session, skip: int = 0, limit: int = 100):
        return OrganizationRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    def get_my_organizations(db: Session, user_id: str):
        return OrganizationRepository.get_by_creator(db, user_id)

    @staticmethod
    def delete_organization(db: Session, org_id: str, user_id: str):
        org = OrganizationRepository.get_by_id(db, org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        if org.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the organization creator can delete it",
            )
        OrganizationRepository.delete(db, org)
        return {"message": "Organization deleted"}
