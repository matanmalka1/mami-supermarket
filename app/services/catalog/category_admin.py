"""Category admin operations."""

from __future__ import annotations

from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Category
from app.schemas.catalog import CategoryResponse
from app.services.audit_service import AuditService
from .mappers import to_category_response


def create_category(name: str, description: str | None) -> CategoryResponse:
    """Create a new category."""
    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()
    AuditService.log_event(
        entity_type="category", action="CREATE", entity_id=category.id
    )
    return to_category_response(category)


def update_category(
    category_id: int, name: str, description: str | None
) -> CategoryResponse:
    """Update an existing category."""
    category = db.session.get(Category, category_id)
    if not category:
        raise DomainError("NOT_FOUND", "Category not found", status_code=404)
    
    old_value = {"name": category.name, "description": category.description}
    category.name = name
    category.description = description
    db.session.add(category)
    db.session.commit()
    
    AuditService.log_event(
        entity_type="category",
        action="UPDATE",
        entity_id=category.id,
        old_value=old_value,
        new_value={"name": name, "description": description},
    )
    return to_category_response(category)


def toggle_category(category_id: int, active: bool) -> CategoryResponse:
    """Toggle category active status."""
    category = db.session.get(Category, category_id)
    if not category:
        raise DomainError("NOT_FOUND", "Category not found", status_code=404)
    
    category.is_active = active
    db.session.add(category)
    db.session.commit()
    
    AuditService.log_event(
        entity_type="category",
        action="DEACTIVATE" if not active else "ACTIVATE",
        entity_id=category.id,
        new_value={"is_active": active},
    )
    return to_category_response(category)
