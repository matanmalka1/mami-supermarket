"""Authentication request/response DTOs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from .common import DefaultModel
from ..models.enums import Role


class RegisterRequest(DefaultModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    role: Role = Role.CUSTOMER


class LoginRequest(DefaultModel):
    email: EmailStr
    password: str


class ChangePasswordRequest(DefaultModel):
    current_password: str
    new_password: str = Field(min_length=8)


class UserResponse(DefaultModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: Role


class AuthResponse(DefaultModel):
    user: UserResponse
    access_token: str
    refresh_token: str | None = None
    expires_at: datetime
