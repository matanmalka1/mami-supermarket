"""User query operations."""

from __future__ import annotations
from sqlalchemy import select, func, or_
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import User
from app.models.enums import Role
from app.schemas.users import UserListItem, UserDetailResponse

def list_users(
    q: str | None = None,
    role: Role | None = None,
    is_active: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[UserListItem], int]:
    """List users with optional filters and pagination."""
    query = select(User)
    
    # Apply filters
    if q:
        search = f"%{q}%"
        query = query.where(
            or_(
                User.email.ilike(search),
                User.full_name.ilike(search),
            )
        )
    
    if role is not None:
        query = query.where(User.role == role)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.session.execute(count_query).scalar_one()
    
    # Apply pagination and ordering
    query = query.order_by(User.created_at.desc()).limit(limit).offset(offset)
    
    users = db.session.execute(query).scalars().all()
    
    return [
        UserListItem(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        for user in users
    ], total

def get_user(user_id: int) -> UserDetailResponse:
    """Get user details by ID."""
    user = db.session.execute(
        select(User).where(User.id == user_id)
    ).scalar_one_or_none()
    
    if not user:
        raise DomainError("USER_NOT_FOUND", "User not found", status_code=404)
    
    return UserDetailResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
        default_branch_id=user.default_branch_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
