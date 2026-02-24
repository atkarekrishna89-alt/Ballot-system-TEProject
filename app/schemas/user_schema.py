"""Pydantic schemas for User operations."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    emp_id: str  # employee identifier used for voter registration


class UserResponse(BaseModel):
    id: str
    email: str
    emp_id: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    roles: List[str] = []

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class AssignRoleRequest(BaseModel):
    role_name: str
