"""Address management service (facade)."""

from __future__ import annotations
from uuid import UUID
from ....schemas.profile import (
    AddressLocationRequest,
    AddressRequest,
    AddressResponse,
    AddressUpdateRequest,
)
from . import query, write
from . import location


class AddressService:
    """Facade for address operations."""
    
    @staticmethod
    def list_addresses(user_id: UUID) -> list[AddressResponse]:
        """List all addresses for a user."""
        return query.list_addresses(user_id)

    @staticmethod
    def create_address(user_id: UUID, data: AddressRequest) -> AddressResponse:
        """Create a new address for a user."""
        return write.create_address(user_id, data)

    @staticmethod
    def update_address(user_id: UUID, address_id: UUID, data: AddressUpdateRequest) -> AddressResponse:
        """Update an existing address."""
        return write.update_address(user_id, address_id, data)

    @staticmethod
    def delete_address(user_id: UUID, address_id: UUID) -> dict:
        """Delete an address."""
        return write.delete_address(user_id, address_id)

    @staticmethod
    def set_default_address(user_id: UUID, address_id: UUID) -> AddressResponse:
        """Set an address as the default."""
        return write.set_default_address(user_id, address_id)

    @staticmethod
    def update_location(user_id: UUID, address_id: UUID, data: AddressLocationRequest) -> AddressResponse:
        """Update address GPS coordinates."""
        return location.update_location(user_id, address_id, data)
