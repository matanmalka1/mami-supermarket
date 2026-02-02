"""User query operations."""

from __future__ import annotations
from sqlalchemy import select, func, or_
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import User
from app.models.enums import Role
from app.schemas.users import UserListItem, UserDetailResponse
from app.services.shared_queries import SharedOperations

def list_users(
    q: str | None = None,
    role: Role | None = None,
    is_active: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[UserListItem], int]:
    """List users with optional filters and pagination."""
    query = select(User)
    
    # Build conditions dict: (condition_check_fn, where_clause)
    conditions = {
        "search": (
            lambda: bool(q),
            or_(
                User.email.ilike(f"%{q}%"),
                User.full_name.ilike(f"%{q}%"),
            ) if q else None,
        ),
        "role": (
            lambda: role is not None,
            User.role == role if role is not None else None,
        ),
        "active": (
            lambda: is_active is not None,
            User.is_active == is_active if is_active is not None else None,
        ),
    }
    
    # Apply filters
    query = SharedOperations.build_filtered_query(query, conditions)
    
    # Apply ordering
    query = query.order_by(User.created_at.desc())
    
    def transform(user):
        return UserListItem(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    
    users, total = SharedOperations.paginate_query(
        base_query=query,
        model_class=User,
        limit=limit,
        offset=offset,
        transform_fn=transform,
    )
    return users, total

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
