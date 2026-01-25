from __future__ import annotations
from uuid import UUID

from ....extensions import db
from ....middleware.error_handler import DomainError
from ....models import Address
from app.schemas.profile import AddressLocationRequest, AddressResponse
from app.services.audit_service import AuditService
from .mappers import address_to_response


def update_location(user_id: UUID, address_id: UUID, data: AddressLocationRequest) -> AddressResponse:
    address = db.session.query(Address).filter_by(id=address_id, user_id=user_id).first()
    if not address:
        raise DomainError("ADDRESS_NOT_FOUND", "Address not found", status_code=404)

    old_value = {"latitude": address.latitude, "longitude": address.longitude}
    address.latitude = data.lat
    address.longitude = data.lng

    db.session.commit()
    AuditService.log_event(
        entity_type="address",
        action="UPDATE_LOCATION",
        actor_user_id=user_id,
        entity_id=address.id,
        old_value=old_value,
        new_value={"latitude": data.lat, "longitude": data.lng},
    )
    return address_to_response(address)
