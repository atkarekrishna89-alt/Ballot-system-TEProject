"""Organization API routes."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role, get_current_user
from app.models.user import User
from app.schemas.organization_schema import OrganizationCreate, OrganizationResponse
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/api/organizations", tags=["Organizations"])


@router.post("/", response_model=OrganizationResponse, status_code=201)
def create_organization(
    data: OrganizationCreate,
    current_user: User = Depends(require_role("SUPER_ADMIN", "ORG_ADMIN")),
    db: Session = Depends(get_db),
):
    """Create a new organization."""
    org = OrganizationService.create_organization(
        db, name=data.name, description=data.description, created_by=current_user.id
    )
    return org


@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all organizations."""
    return OrganizationService.get_all_organizations(db, skip=skip, limit=limit)


@router.get("/mine", response_model=List[OrganizationResponse])
def my_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List organizations created by the current user."""
    return OrganizationService.get_my_organizations(db, current_user.id)


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get organization by ID."""
    return OrganizationService.get_organization(db, org_id)


@router.delete("/{org_id}")
def delete_organization(
    org_id: str,
    current_user: User = Depends(require_role("SUPER_ADMIN", "ORG_ADMIN")),
    db: Session = Depends(get_db),
):
    """Delete an organization."""
    return OrganizationService.delete_organization(db, org_id, current_user.id)
