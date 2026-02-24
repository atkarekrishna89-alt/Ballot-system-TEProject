"""User management API routes (admin-only)."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.schemas.user_schema import UserResponse, AssignRoleRequest
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role("SUPER_ADMIN", "ORG_ADMIN")),
    db: Session = Depends(get_db),
):
    """List all users (admin only)."""
    users = UserRepository.get_all(db, skip=skip, limit=limit)
    result = []
    for user in users:
        roles = UserRepository.get_user_roles(db, user.id)
        result.append(
            UserResponse(
                id=user.id,
                email=user.email,
                emp_id=user.emp_id,
                full_name=user.full_name,
                is_active=user.is_active,
                created_at=user.created_at,
                roles=roles,
            )
        )
    return result


@router.put("/{user_id}/roles")
def assign_role(
    user_id: str,
    data: AssignRoleRequest,
    current_user: User = Depends(require_role("SUPER_ADMIN")),
    db: Session = Depends(get_db),
):
    """Assign a role to a user (super admin only)."""
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    success = UserRepository.assign_role(db, user_id, data.role_name)
    if not success:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")

    roles = UserRepository.get_user_roles(db, user_id)
    return {"message": f"Role {data.role_name} assigned", "roles": roles}


@router.get("/emp/{emp_id}", response_model=UserResponse)
def get_user_by_emp(emp_id: str,
                    current_user: User = Depends(require_role("SUPER_ADMIN", "ORG_ADMIN")),
                    db: Session = Depends(get_db)):
    """Lookup a user by employee ID (admins only)."""
    user = UserRepository.get_by_emp_id(db, emp_id)
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    roles = UserRepository.get_user_roles(db, user.id)
    return UserResponse(
        id=user.id,
        email=user.email,
        emp_id=user.emp_id,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
        roles=roles,
    )


@router.delete("/{user_id}/roles/{role_name}")
def remove_role(
    user_id: str,
    role_name: str,
    current_user: User = Depends(require_role("SUPER_ADMIN")),
    db: Session = Depends(get_db),
):
    """Remove a role from a user (super admin only)."""
    UserRepository.remove_role(db, user_id, role_name)
    roles = UserRepository.get_user_roles(db, user_id)
    return {"message": f"Role {role_name} removed", "roles": roles}
