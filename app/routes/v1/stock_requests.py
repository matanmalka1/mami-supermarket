"""Stock request endpoints for employees and managers/admins."""

from __future__ import annotations

from uuid import UUID

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.middleware.auth import require_role
from app.middleware.error_handler import DomainError
from app.models.enums import Role, StockRequestStatus
from app.schemas.stock_requests import (
    BulkReviewRequest,
    StockRequestCreateRequest,
    StockRequestReviewRequest,
)
from app.services.stock_requests import StockRequestService
from app.utils.responses import pagination_envelope, success_envelope

blueprint = Blueprint("stock_requests", __name__)


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


@blueprint.post("")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def create_stock_request():
    payload = StockRequestCreateRequest.model_validate(request.get_json() or {})
    result = StockRequestService.create_request(_current_user_id(), payload)
    return jsonify(success_envelope(result)), 201


@blueprint.get("/my")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def list_my_requests():
    limit, offset = _pagination()
    rows, total = StockRequestService.list_my(_current_user_id(), limit, offset)
    return jsonify(success_envelope(rows, pagination_envelope(total, limit, offset)))


@blueprint.get("/admin")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def list_admin_requests():
    status_val = request.args.get("status")
    try:
        status = StockRequestStatus(status_val) if status_val else None
    except ValueError:
        raise DomainError("BAD_REQUEST", "Invalid status filter", status_code=400)
    limit, offset = _pagination()
    rows, total = StockRequestService.list_admin(status, limit, offset)
    return jsonify(success_envelope(rows, pagination_envelope(total, limit, offset)))


@blueprint.patch("/admin/<uuid:request_id>/review")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def review_request(request_id: UUID):
    payload = StockRequestReviewRequest.model_validate(request.get_json() or {})
    result = StockRequestService.review(
        request_id,
        payload.status,
        payload.approved_quantity,
        payload.rejection_reason,
        _current_user_id(),
    )
    return jsonify(success_envelope(result))


@blueprint.patch("/admin/bulk-review")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def bulk_review():
    payload = BulkReviewRequest.model_validate(request.get_json() or {})
    results = StockRequestService.bulk_review(payload, _current_user_id())
    return jsonify(success_envelope({"results": results}))
