"""Shared database queries and operations that can be reused across services."""

from __future__ import annotations
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import User, Address
from app.schemas.profile import UserProfileResponse

class SharedQueries:
    """Common database queries used across multiple services."""

    @staticmethod
    def get_active_user_by_id(user_id: int) -> User:
        """Fetch active user by ID."""
        user = db.session.query(User).filter_by(id=user_id, is_active=True).first()
        if not user:
            raise DomainError("USER_NOT_FOUND", "User not found", status_code=404)
        return user

    @staticmethod
    def get_user_by_email(email: str) -> User | None:
        """Fetch user by email."""
        return db.session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

    @staticmethod
    def user_to_profile_response(user: User) -> UserProfileResponse:
        """Convert User model to UserProfileResponse."""
        return UserProfileResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role.value,
        )

    @staticmethod
    def get_address_by_id_and_user(address_id: int, user_id: int) -> Address:
        """Fetch address by ID and user ID."""
        address = db.session.query(Address).filter_by(id=address_id, user_id=user_id).first()
        if not address:
            raise DomainError("ADDRESS_NOT_FOUND", "Address not found", status_code=404)
        return address

class SharedOperations:
    """Common database operations with error handling and audit logging."""

    @staticmethod
    def commit_with_audit(
        entity_type: str,
        action: str,
        entity_id: int,
        actor_user_id: int | None = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
        error_message: str = "Database operation failed",
    ) -> None:
        from app.services.audit_service import AuditService
        
        try:
            db.session.commit()
            AuditService.log_event(
                entity_type=entity_type,
                action=action,
                entity_id=entity_id,
                actor_user_id=actor_user_id,
                old_value=old_value,
                new_value=new_value,
            )
        except IntegrityError as exc:
            db.session.rollback()
            raise DomainError("DATABASE_ERROR", error_message, details={"error": str(exc)})

    @staticmethod
    def paginate_query(
        base_query,
        model_class,
        limit: int = 50,
        offset: int = 0,
        transform_fn=None,
    ) -> tuple[list, int]:
      
        total = db.session.scalar(
            select(func.count()).select_from(base_query.subquery())
        )
        rows = db.session.execute(
            base_query.offset(offset).limit(limit)
        ).scalars().all()
        
        if transform_fn:
            rows = [transform_fn(row) for row in rows]
        
        return rows, total or 0

    @staticmethod
    def build_filtered_query(base_query, conditions: dict):
        for check_fn, where_clause in conditions.values():
            if check_fn():
                base_query = base_query.where(where_clause)
        return base_query

    @staticmethod
    def unset_default_for_user(user_id, model_class, entity_id: int | None = None):
        try:
            query = db.session.query(model_class).filter_by(user_id=user_id, is_default=True)
            if entity_id:
                query = query.filter(model_class.id != entity_id)
            query.update({"is_default": False})
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise DomainError(
                "DATABASE_ERROR",
                f"Could not update default {model_class.__name__}",
                details={"error": str(exc)},
            )