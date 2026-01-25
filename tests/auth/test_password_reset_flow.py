import hashlib

from app.schemas.auth import RegisterRequest
from app.services.auth_service import AuthService
from app.services.password_reset_service import PasswordResetService
from app.models.password_reset_token import PasswordResetToken


def _register_user(test_app):
    payload = RegisterRequest(email="resetuser@example.com", password="Secret123!", full_name="Reset User")
    with test_app.app_context():
        user = AuthService.register(payload)
        user_id = user.id
    return user_id, payload.email


def test_forgot_password_returns_token_and_persists_hash(client, session, test_app):
    user_id, email = _register_user(test_app)

    resp = client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert resp.status_code == 200
    body = resp.get_json().get("data")
    assert body.get("reset_token")

    token_hash = hashlib.sha256(body["reset_token"].encode()).hexdigest()
    stored = session.query(PasswordResetToken).filter_by(user_id=user_id).first()
    assert stored and stored.token_hash == token_hash


def test_reset_password_consumes_token_and_changes_password(client, session, test_app):
    user_id, email = _register_user(test_app)
    token = PasswordResetService.create_token(user_id)

    reset_resp = client.post(
        "/api/v1/auth/reset-password",
        json={"email": email, "token": token, "new_password": "NewSecret123!"},
    )
    assert reset_resp.status_code == 200

    with test_app.app_context():
        authenticated = AuthService.authenticate(email, "NewSecret123!")
    assert str(authenticated.id) == str(user_id)
