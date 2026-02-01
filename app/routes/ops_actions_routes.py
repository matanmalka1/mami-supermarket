"""Admin-only ops actions that currently return placeholder data."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.middleware.auth import require_role
from app.models.enums import Role
from app.schemas.ops import DamageReportRequest
from app.utils.request_utils import current_user_id
from app.utils.responses import success_envelope
from app.services.ops_actions_service import OpsActionsService

blueprint = Blueprint("ops_actions", __name__)


## UPDATE (Sync Order)

@blueprint.post("/orders/<int:order_id>/sync")
@jwt_required()
@require_role(Role.ADMIN)
def sync_order(order_id: int):
    user_id = current_user_id()
    result = OpsActionsService.sync_order(order_id, user_id)
    return jsonify(success_envelope(result))


## CREATE (Report Damage)

@blueprint.post("/orders/<int:order_id>/items/<int:item_id>/report-damage")
@jwt_required()
@require_role(Role.ADMIN)
def report_damage(order_id: int, item_id: int):
    payload = DamageReportRequest.model_validate(request.get_json() or {})
    user_id = current_user_id()
    result = OpsActionsService.report_damage(order_id, item_id, payload, user_id)
    return jsonify(success_envelope(result)), 201
