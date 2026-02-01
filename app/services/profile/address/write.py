"""Address write service."""

from __future__ import annotations
from uuid import UUID

from ....schemas.profile import AddressRequest, AddressResponse, AddressUpdateRequest
from ...audit_service import AuditService
from .mappers import address_to_response
from . import operations


def create_address(user_id: UUID, data: AddressRequest) -> AddressResponse:
    """Create a new address for a user."""
    address = operations.create_address_record(user_id, data)
    
    AuditService.log_event(
        entity_type="address",
        action="CREATE",
        entity_id=address.id,
        actor_user_id=user_id,
        new_value={
            "address_line": data.address_line,
            "city": data.city,
            "postal_code": data.postal_code,
            "country": data.country,
            "is_default": data.is_default,
        },
    )
    
    return address_to_response(address)


def update_address(
    user_id: UUID, address_id: UUID, data: AddressUpdateRequest
) -> AddressResponse:
    """Update an existing address."""
    address, old_values, new_values = operations.update_address_record(
        user_id, address_id, data
    )
    
    if new_values:
        AuditService.log_event(
            entity_type="address",
            action="UPDATE",
            entity_id=address.id,
            actor_user_id=user_id,
            old_value=old_values,
            new_value=new_values,
        )
    
    return address_to_response(address)


def delete_address(user_id: UUID, address_id: UUID) -> dict:
    """Delete an address."""
    old_value = operations.delete_address_record(user_id, address_id)
    
    AuditService.log_event(
        entity_type="address",
        action="DELETE",
        entity_id=address_id,
        actor_user_id=user_id,
        old_value=old_value,
    )
    
    return {"message": "Address deleted successfully"}


def set_default_address(user_id: UUID, address_id: UUID) -> AddressResponse:
    """Set an address as the default."""
    address, old_value = operations.set_default_address_record(user_id, address_id)
    
    AuditService.log_event(
        entity_type="address",
        action="SET_DEFAULT",
        entity_id=address.id,
        actor_user_id=user_id,
        old_value=old_value,
        new_value={"is_default": True},
    )
    
    return address_to_response(address)

