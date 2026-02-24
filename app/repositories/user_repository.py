"""Repository layer for User and Role database operations."""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role, UserRole


class UserRepository:
    """Data access for User operations."""

    @staticmethod
    def create(db: Session, email: str, password_hash: str, full_name: Optional[str] = None, emp_id: Optional[str] = None) -> User:
        user = User(email=email, password_hash=password_hash, full_name=full_name, emp_id=emp_id)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_emp_id(db: Session, emp_id: str) -> Optional[User]:
        return db.query(User).filter(User.emp_id == emp_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_roles(db: Session, user_id: str) -> List[str]:
        roles = (
            db.query(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user_id)
            .all()
        )
        return [r.name for r in roles]

    @staticmethod
    def assign_role(db: Session, user_id: str, role_name: str) -> bool:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            return False

        existing = (
            db.query(UserRole)
            .filter(UserRole.user_id == user_id, UserRole.role_id == role.id)
            .first()
        )
        if existing:
            return True  # Already assigned

        user_role = UserRole(user_id=user_id, role_id=role.id)
        db.add(user_role)
        db.commit()
        return True

    @staticmethod
    def remove_role(db: Session, user_id: str, role_name: str) -> bool:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            return False

        user_role = (
            db.query(UserRole)
            .filter(UserRole.user_id == user_id, UserRole.role_id == role.id)
            .first()
        )
        if user_role:
            db.delete(user_role)
            db.commit()
        return True


class RoleRepository:
    """Data access for Role operations."""

    @staticmethod
    def get_or_create(db: Session, name: str) -> Role:
        role = db.query(Role).filter(Role.name == name).first()
        if not role:
            role = Role(name=name)
            db.add(role)
            db.commit()
            db.refresh(role)
        return role

    @staticmethod
    def get_all(db: Session) -> List[Role]:
        return db.query(Role).all()
