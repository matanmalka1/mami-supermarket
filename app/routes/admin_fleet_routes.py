from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.middleware.auth import require_role
from app.models.enums import Role
from app.utils.responses import success_envelope
from app.services.fleet_service import get_fleet_status as fleet_status_service

blueprint = Blueprint("admin_fleet", __name__, url_prefix="/api/v1/admin")

@blueprint.get("/fleet/status")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def get_fleet_status():
    status = fleet_status_service()
    return jsonify(success_envelope(status))
