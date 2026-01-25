"""Address mappers."""

from __future__ import annotations
from ....models import Address
from ....schemas.profile import AddressResponse


def address_to_response(address: Address) -> AddressResponse:
    """Convert Address model to response schema."""
    return AddressResponse(
        id=address.id,
        user_id=address.user_id,
        address_line=address.address_line,
        city=address.city,
        postal_code=address.postal_code,
        country=address.country,
        is_default=address.is_default,
        lat=address.latitude,
        lng=address.longitude,
    )
