"""Authentication endpoints."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..middleware.error_handler import DomainError
from ..utils.responses import success_envelope
from ..schemas.auth import (
    AuthResponse,
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
)
from ..services.auth import AuthService

blueprint = Blueprint("auth", __name__)


def _parse_payload(request_body: dict | None) -> dict:
    if not request_body:
        raise DomainError("BAD_REQUEST", "Missing JSON body", status_code=400)
    return request_body


def _build_response(payload: AuthResponse):
    return jsonify(success_envelope(payload.model_dump()))


@blueprint.post("/register")
def register():
    payload = RegisterRequest.model_validate(_parse_payload(request.get_json()))
    user = AuthService.register(payload)
    response = AuthService.build_auth_response(user)
    return _build_response(response), 201


@blueprint.post("/login")
def login():
    payload = LoginRequest.model_validate(_parse_payload(request.get_json()))
    user = AuthService.authenticate(payload.email, payload.password)
    response = AuthService.build_auth_response(user)
    return _build_response(response)


@blueprint.post("/change-password")
@jwt_required()
def change_password():
    payload = ChangePasswordRequest.model_validate(_parse_payload(request.get_json()))
    user_id = get_jwt_identity()
    AuthService.change_password(user_id, payload.current_password, payload.new_password)
    return jsonify(success_envelope({"message": "Password updated"}))
