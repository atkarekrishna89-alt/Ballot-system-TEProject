"""Service layer for authentication business logic."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.repositories.user_repository import UserRepository, RoleRepository


class AuthService:
    """Business logic for authentication operations."""

    @staticmethod
    def register(db: Session, email: str, password: str, full_name: str = None, emp_id: str = None):
        """Register a new user with VOTER role."""
        existing = UserRepository.get_by_email(db, email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        if emp_id:
            existing_emp = UserRepository.get_by_emp_id(db, emp_id)
            if existing_emp:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Employee ID already registered",
                )

        password_hash = hash_password(password)
        user = UserRepository.create(db, email=email, password_hash=password_hash, full_name=full_name, emp_id=emp_id)

        # Assign default VOTER role
        UserRepository.assign_role(db, user.id, "VOTER")

        roles = UserRepository.get_user_roles(db, user.id)
        return user, roles

    @staticmethod
    def login(db: Session, email: str, password: str):
        """Authenticate user and return tokens."""
        user = UserRepository.get_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        roles = UserRepository.get_user_roles(db, user.id)
        token_data = {"sub": user.id, "email": user.email, "roles": roles}

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def refresh_token(db: Session, refresh_token_str: str):
        """Issue new access token using a valid refresh token."""
        payload = decode_refresh_token(refresh_token_str)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user_id = payload.get("sub")
        user = UserRepository.get_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        roles = UserRepository.get_user_roles(db, user.id)
        token_data = {"sub": user.id, "email": user.email, "roles": roles}

        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
