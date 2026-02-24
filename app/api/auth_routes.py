"""Authentication API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth_schema import LoginRequest, TokenResponse, RefreshRequest
from app.schemas.user_schema import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    user, roles = AuthService.register(
        db,
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        emp_id=data.emp_id,
    )
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
        roles=roles,
    )


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Login and get access + refresh tokens."""
    return AuthService.login(db, email=data.email, password=data.password)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    """Refresh access token."""
    return AuthService.refresh_token(db, data.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current authenticated user info."""
    roles = UserRepository.get_user_roles(db, current_user.id)
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        emp_id=current_user.emp_id,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        roles=roles,
    )
