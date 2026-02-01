"""Address CRUD operations."""

from __future__ import annotations
from uuid import UUID
from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ....middleware.error_handler import DomainError
from ....models import Address
from ....schemas.profile import AddressRequest, AddressUpdateRequest


def create_address_record(user_id: UUID, data: AddressRequest) -> Address:
    """Create address record in database."""
    if data.is_default:
        db.session.query(Address).filter_by(
            user_id=user_id, is_default=True
        ).update({"is_default": False})
    
    address = Address(
        user_id=user_id,
        address_line=data.address_line,
        city=data.city,
        postal_code=data.postal_code,
        country=data.country,
        is_default=data.is_default,
    )
    
    db.session.add(address)
    
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise DomainError(
            "DATABASE_ERROR",
            "Could not create address",
            details={"error": str(exc)},
        )
    
    return address


def update_address_record(
    user_id: UUID, address_id: UUID, data: AddressUpdateRequest
) -> tuple[Address, dict, dict]:
    """Update address record and return old/new values."""
    address = db.session.query(Address).filter_by(
        id=address_id, user_id=user_id
    ).first()
    
    if not address:
        raise DomainError("ADDRESS_NOT_FOUND", "Address not found", status_code=404)
    
    old_values = {}
    new_values = {}
    
    if data.address_line is not None:
        old_values["address_line"] = address.address_line
        address.address_line = data.address_line
        new_values["address_line"] = data.address_line
    
    if data.city is not None:
        old_values["city"] = address.city
        address.city = data.city
        new_values["city"] = data.city
    
    if data.postal_code is not None:
        old_values["postal_code"] = address.postal_code
        address.postal_code = data.postal_code
        new_values["postal_code"] = data.postal_code
    
    if data.country is not None:
        old_values["country"] = address.country
        address.country = data.country
        new_values["country"] = data.country
    
    if new_values:
        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise DomainError(
                "DATABASE_ERROR",
                "Could not update address",
                details={"error": str(exc)},
            )
    
    return address, old_values, new_values


def delete_address_record(user_id: UUID, address_id: UUID) -> dict:
    """Delete address record and return old value."""
    address = db.session.query(Address).filter_by(
        id=address_id, user_id=user_id
    ).first()
    
    if not address:
        raise DomainError("ADDRESS_NOT_FOUND", "Address not found", status_code=404)
    
    old_value = {
        "address_line": address.address_line,
        "city": address.city,
        "postal_code": address.postal_code,
        "country": address.country,
        "is_default": address.is_default,
    }
    
    db.session.delete(address)
    
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise DomainError(
            "DATABASE_ERROR",
            "Could not delete address",
            details={"error": str(exc)},
        )
    
    return old_value


def set_default_address_record(user_id: UUID, address_id: UUID) -> tuple[Address, dict]:
    """Set address as default and return old value."""
    address = db.session.query(Address).filter_by(
        id=address_id, user_id=user_id
    ).first()
    
    if not address:
        raise DomainError("ADDRESS_NOT_FOUND", "Address not found", status_code=404)
    
    db.session.query(Address).filter_by(
        user_id=user_id, is_default=True
    ).update({"is_default": False})
    
    old_value = {"is_default": address.is_default}
    address.is_default = True
    
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise DomainError(
            "DATABASE_ERROR",
            "Could not set default address",
            details={"error": str(exc)},
        )
    
    return address, old_value
