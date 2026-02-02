"""Address management service."""

from __future__ import annotations
from typing import Any

from ....extensions import db
from ....middleware.error_handler import DomainError
from ....models import Address
from ....schemas.profile import (
    AddressLocationRequest,
    AddressRequest,
    AddressResponse,
    AddressUpdateRequest,
)
from ...shared_queries import SharedQueries, SharedOperations
from .mappers import address_to_response


class AddressService:
    """Address operations used by the profile routes."""

    _ADDRESS_FIELDS = ("address_line", "city", "postal_code", "country")
    _ENTITY_TYPE = "address"

    @staticmethod
    def _update_field(
        address: Address,
        payload: Any,
        field: str,
        old_values: dict[str, Any],
        new_values: dict[str, Any],
    ) -> None:
        """Update a single address field if provided."""
        value = getattr(payload, field, None)
        if value is None:
            return
        old_values[field] = getattr(address, field)
        setattr(address, field, value)
        new_values[field] = value

    @staticmethod
    def list_addresses(user_id: int) -> list[AddressResponse]:
        addresses = (
            db.session.query(Address)
            .filter_by(user_id=user_id)
            .order_by(Address.is_default.desc(), Address.created_at.desc())
            .all()
        )
        return [address_to_response(addr) for addr in addresses]

    @staticmethod
    def create_address(user_id: int, data: AddressRequest) -> AddressResponse:
        if data.is_default:
            SharedOperations.unset_default_for_user(user_id, Address)
        
        address = Address(
            user_id=user_id,
            address_line=data.address_line,
            city=data.city,
            postal_code=data.postal_code,
            country=data.country,
            is_default=data.is_default,
        )
        db.session.add(address)
        db.session.flush() 
        db.session.refresh(address) 
        
        new_value = {
            "address_line": data.address_line,
            "city": data.city,
            "postal_code": data.postal_code,
            "country": data.country,
            "is_default": data.is_default,
        }
        
        SharedOperations.commit_with_audit(
            entity_type=AddressService._ENTITY_TYPE,
            action="CREATE",
            entity_id=address.id,
            actor_user_id=user_id,
            new_value=new_value,
            error_message="Could not create address",
        )
        return address_to_response(address)

    @staticmethod
    def update_address(user_id: int, address_id: int, data: AddressUpdateRequest) -> AddressResponse:
        address = SharedQueries.get_address_by_id_and_user(address_id, user_id)
        old_values: dict[str, Any] = {}
        new_values: dict[str, Any] = {}
        for field in AddressService._ADDRESS_FIELDS:
            AddressService._update_field(address, data, field, old_values, new_values)
        if not new_values:
            return address_to_response(address)
        SharedOperations.commit_with_audit(
            entity_type=AddressService._ENTITY_TYPE,
            action="UPDATE",
            entity_id=address.id,
            actor_user_id=user_id,
            old_value=old_values,
            new_value=new_values,
            error_message="Could not update address",
        )
        return address_to_response(address)

    @staticmethod
    def delete_address(user_id: int, address_id: int) -> dict[str, str]:
        address = SharedQueries.get_address_by_id_and_user(address_id, user_id)
        old_value = {
            "address_line": address.address_line,
            "city": address.city,
            "postal_code": address.postal_code,
            "country": address.country,
            "is_default": address.is_default,
        }
        db.session.delete(address)
        SharedOperations.commit_with_audit(
            entity_type=AddressService._ENTITY_TYPE,
            action="DELETE",
            entity_id=address_id,
            actor_user_id=user_id,
            old_value=old_value,
            error_message="Could not delete address",
        )
        return {"message": "Address deleted successfully"}

    @staticmethod
    def set_default_address(user_id: int, address_id: int) -> AddressResponse:
        address = SharedQueries.get_address_by_id_and_user(address_id, user_id)
        SharedOperations.unset_default_for_user(user_id, Address, entity_id=address_id)
        
        old_value = {"is_default": address.is_default}
        address.is_default = True
        SharedOperations.commit_with_audit(
            entity_type=AddressService._ENTITY_TYPE,
            action="SET_DEFAULT",
            entity_id=address.id,
            actor_user_id=user_id,
            old_value=old_value,
            new_value={"is_default": True},
            error_message="Could not set default address",
        )
        return address_to_response(address)

    @staticmethod
    def update_location(user_id: int, address_id: int, data: AddressLocationRequest) -> AddressResponse:
        address = SharedQueries.get_address_by_id_and_user(address_id, user_id)
        old_value = {"latitude": address.latitude, "longitude": address.longitude}
        address.latitude = data.lat
        address.longitude = data.lng
        
        SharedOperations.commit_with_audit(
            entity_type=AddressService._ENTITY_TYPE,
            action="UPDATE_LOCATION",
            entity_id=address.id,
            actor_user_id=user_id,
            old_value=old_value,
            new_value={"latitude": data.lat, "longitude": data.lng},
            error_message="Could not update location",
        )
        return address_to_response(address)
