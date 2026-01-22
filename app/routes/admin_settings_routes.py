from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.middleware.auth import require_role
from app.models.enums import Role
from app.utils.responses import success_envelope

blueprint = Blueprint("admin_settings", __name__, url_prefix="/api/v1/admin")

@blueprint.get("/settings")
@jwt_required()
@require_role(Role.ADMIN)
def get_settings():
    config = current_app.config
    settings = {
        "delivery_min": config.get("DELIVERY_MIN_TOTAL", 150),
        "delivery_fee": config.get("DELIVERY_FEE_UNDER_MIN", 30),
        "slots": "06:00-22:00",
    }
    return jsonify(success_envelope(settings))
