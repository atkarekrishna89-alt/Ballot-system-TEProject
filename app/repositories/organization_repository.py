"""Repository layer for Organization database operations."""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.organization import Organization


class OrganizationRepository:
    """Data access for Organization operations."""

    @staticmethod
    def create(db: Session, name: str, description: Optional[str], created_by: str) -> Organization:
        org = Organization(name=name, description=description, created_by=created_by)
        db.add(org)
        db.commit()
        db.refresh(org)
        return org

    @staticmethod
    def get_by_id(db: Session, org_id: str) -> Optional[Organization]:
        return db.query(Organization).filter(Organization.id == org_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Organization]:
        return db.query(Organization).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_creator(db: Session, user_id: str) -> List[Organization]:
        return db.query(Organization).filter(Organization.created_by == user_id).all()

    @staticmethod
    def update(db: Session, org: Organization, **kwargs) -> Organization:
        for key, value in kwargs.items():
            if value is not None and hasattr(org, key):
                setattr(org, key, value)
        db.commit()
        db.refresh(org)
        return org

    @staticmethod
    def delete(db: Session, org: Organization) -> None:
        db.delete(org)
        db.commit()
