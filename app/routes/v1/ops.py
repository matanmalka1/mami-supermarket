"""Operations endpoints for employees/managers."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.middleware.auth import require_role
from app.middleware.error_handler import DomainError
from app.models.enums import OrderStatus, Role
from app.services.ops import OpsOrderService
from app.utils.responses import pagination_envelope, success_envelope

blueprint = Blueprint("ops", __name__)


def _current_user_id() -> UUID:
    user_id = get_jwt_identity()
    if not user_id:
        raise DomainError("AUTH_REQUIRED", "Authentication required", status_code=401)
    return UUID(user_id)


def _parse_filters() -> tuple[OrderStatus | None, datetime | None, datetime | None, int, int]:
    status_val = request.args.get("status")
    try:
        status = OrderStatus(status_val) if status_val else None
    except ValueError:
        raise DomainError("BAD_REQUEST", "Invalid status filter", status_code=400)
    date_from = request.args.get("dateFrom")
    date_to = request.args.get("dateTo")
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
    except (TypeError, ValueError):
        raise DomainError("BAD_REQUEST", "Invalid pagination parameters", status_code=400)
    def _parse_dt(val: str | None):
        if not val:
            return None
        try:
            return datetime.fromisoformat(val)
        except ValueError:
            raise DomainError("BAD_REQUEST", "Invalid date format; use ISO 8601", status_code=400)
    return status, _parse_dt(date_from), _parse_dt(date_to), limit, offset


@blueprint.get("/orders")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def list_orders():
    status, date_from, date_to, limit, offset = _parse_filters()
    orders, total = OpsOrderService.list_orders(status, date_from, date_to, limit, offset)
    return jsonify(success_envelope(orders, pagination_envelope(total, limit, offset)))


@blueprint.get("/orders/<uuid:order_id>")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def get_order(order_id: UUID):
    order = OpsOrderService.get_order(order_id)
    return jsonify(success_envelope(order))


@blueprint.patch("/orders/<uuid:order_id>/items/<uuid:item_id>/picked-status")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def update_picked_status(order_id: UUID, item_id: UUID):
    payload = request.get_json() or {}
    new_status = payload.get("picked_status")
    if not new_status:
        raise DomainError("BAD_REQUEST", "picked_status is required", status_code=400)
    order = OpsOrderService.update_item_status(order_id, item_id, new_status, _current_user_id())
    return jsonify(success_envelope(order))


@blueprint.patch("/orders/<uuid:order_id>/status")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def update_order_status(order_id: UUID):
    payload = request.get_json() or {}
    new_status = payload.get("status")
    if not new_status:
        raise DomainError("BAD_REQUEST", "status is required", status_code=400)
    user = getattr(g, "current_user", None)
    actor_role = user.role if user else Role.EMPLOYEE
    order = OpsOrderService.update_order_status(order_id, new_status, _current_user_id(), actor_role)
    return jsonify(success_envelope(order))
