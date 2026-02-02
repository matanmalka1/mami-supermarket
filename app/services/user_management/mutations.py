"""User update operations."""

from __future__ import annotations
from sqlalchemy import select
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import User
from app.schemas.users import UserDetailResponse, UpdateUserRequest
from app.services.shared_queries import SharedOperations


def update_user(user_id: int, payload: UpdateUserRequest) -> UserDetailResponse:
    """Update user fields."""
    current_user_id = get_jwt_identity()
    
    user = db.session.execute(
        select(User).where(User.id == user_id)
    ).scalar_one_or_none()
    
    if not user:
        raise DomainError("USER_NOT_FOUND", "User not found", status_code=404)
    
    if str(user.id) == current_user_id and payload.role is not None:
        raise DomainError(
            "CANNOT_MODIFY_SELF_ROLE",
            "Cannot modify your own role",
            status_code=403,
        )
    
    old_values = {}
    new_values = {}
    
    # Update role
    if payload.role is not None and payload.role != user.role:
        old_values["role"] = user.role.value
        new_values["role"] = payload.role.value
        user.role = payload.role
    
    # Update is_active
    if payload.is_active is not None and payload.is_active != user.is_active:
        old_values["is_active"] = user.is_active
        new_values["is_active"] = payload.is_active
        user.is_active = payload.is_active
    
    # Update full_name
    if payload.full_name is not None and payload.full_name != user.full_name:
        old_values["full_name"] = user.full_name
        new_values["full_name"] = payload.full_name
        user.full_name = payload.full_name
    
    # Update phone
    if payload.phone is not None and payload.phone != user.phone:
        old_values["phone"] = user.phone
        new_values["phone"] = payload.phone
        user.phone = payload.phone
    
    # Log audit if changes were made
    if old_values:
        SharedOperations.commit_with_audit(
            entity_type="User",
            action="USER_UPDATED",
            entity_id=user.id,
            actor_user_id=int(current_user_id),
            old_value=old_values,
            new_value=new_values,
            error_message="Could not update user",
        )
    else:
        db.session.commit()
    
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


def toggle_user(user_id: int, active: bool) -> UserDetailResponse:
    """Toggle user active status."""
    current_user_id = get_jwt_identity()
    
    user = db.session.execute(
        select(User).where(User.id == user_id)
    ).scalar_one_or_none()
    
    if not user:
        raise DomainError("USER_NOT_FOUND", "User not found", status_code=404)
    
    # Prevent admins from deactivating themselves
    if str(user.id) == current_user_id and not active:
        raise DomainError(
            "CANNOT_DEACTIVATE_SELF",
            "Cannot deactivate your own account",
            status_code=403,
        )
    
    if user.is_active != active:
        old_value = {"is_active": user.is_active}
        new_value = {"is_active": active}
        user.is_active = active
        
        SharedOperations.commit_with_audit(
            entity_type="User",
            action="USER_TOGGLED",
            entity_id=user.id,
            actor_user_id=int(current_user_id),
            old_value=old_value,
            new_value=new_value,
            error_message="Could not toggle user status",
        )
    else:
        db.session.commit()
    
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
