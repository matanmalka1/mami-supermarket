"""Customer order endpoints."""

from __future__ import annotations

from uuid import UUID

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.middleware.error_handler import DomainError
from app.services.order import OrderService
from app.utils.responses import pagination_envelope, success_envelope

blueprint = Blueprint("orders", __name__)


def _current_user_id() -> UUID:
    user_id = get_jwt_identity()
    if not user_id:
        raise DomainError("AUTH_REQUIRED", "Authentication required", status_code=401)
    return UUID(user_id)


def _pagination() -> tuple[int, int]:
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
    except (TypeError, ValueError):
        raise DomainError("BAD_REQUEST", "Invalid pagination parameters", status_code=400)
    return limit, offset


@blueprint.get("")
@jwt_required()
def list_orders():
    user_id = _current_user_id()
    limit, offset = _pagination()
    orders, total = OrderService.list_orders(user_id, limit, offset)
    return jsonify(success_envelope(orders, pagination_envelope(total, limit, offset)))


@blueprint.get("/<uuid:order_id>")
@jwt_required()
def get_order(order_id: UUID):
    user_id = _current_user_id()
    order = OrderService.get_order(order_id, user_id)
    return jsonify(success_envelope(order))


@blueprint.post("/<uuid:order_id>/cancel")
@jwt_required()
def cancel_order(order_id: UUID):
    user_id = _current_user_id()
    payload = OrderService.cancel_order(order_id, user_id)
    return jsonify(success_envelope(payload))
