"""Temporary OTP verification endpoint (DEV only)."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from app.middleware.error_handler import DomainError
from app.schemas.auth import VerifyRegisterOTPRequest
from app.utils.responses import success_envelope

blueprint = Blueprint("auth_otp", __name__)


@blueprint.post("/register/verify-otp")
def verify_register_otp():
    """Return a verified flag when in non-production environments."""
    payload = VerifyRegisterOTPRequest.model_validate(request.get_json() or {})
    env = current_app.config.get("APP_ENV", "production").lower()
    if env not in {"development", "testing"} and not current_app.config.get("TESTING"):
        raise DomainError(
            "OTP_NOT_ENVIRONMENT",
            "OTP verification is disabled outside development/testing (TODO: wire real service)",
            status_code=403,
        )
    return jsonify(success_envelope({"verified": True}))
