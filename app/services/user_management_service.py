"""User management service for admin operations."""

from __future__ import annotations
from app.schemas.users import UserListItem, UserDetailResponse, UpdateUserRequest
from app.models.enums import Role
from .user_management import queries, mutations


class UserManagementService:
    """Service for admin user management operations."""

    @staticmethod
    def list_users(
        q: str | None = None,
        role: Role | None = None,
        is_active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[UserListItem], int]:
        """List users with optional filters and pagination."""
        return queries.list_users(q, role, is_active, limit, offset)

    @staticmethod
    def get_user(user_id: int) -> UserDetailResponse:
        """Get user details by ID."""
        return queries.get_user(user_id)

    @staticmethod
    def update_user(user_id: int, payload: UpdateUserRequest) -> UserDetailResponse:
        """Update user fields."""
        return mutations.update_user(user_id, payload)

    @staticmethod
    def toggle_user(user_id: int, active: bool) -> UserDetailResponse:
        """Toggle user active status."""
        return mutations.toggle_user(user_id, active)
