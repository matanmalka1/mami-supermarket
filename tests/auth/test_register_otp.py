"""Tests for the temporary OTP verification endpoint."""

def test_verify_register_otp_allowed_in_testing(client):
    response = client.post(
        "/api/v1/auth/register/verify-otp",
        json={"email": "otp@example.com", "code": "1234"},
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["verified"] is True

def test_verify_register_otp_blocked_in_production(test_app, client):
    original_testing = test_app.config.get("TESTING")
    original_env = test_app.config.get("APP_ENV")
    test_app.config["TESTING"] = False
    test_app.config["APP_ENV"] = "production"
    try:
        response = client.post(
            "/api/v1/auth/register/verify-otp",
            json={"email": "otp@example.com", "code": "1234"},
        )
        assert response.status_code == 403
    finally:
        test_app.config["TESTING"] = original_testing
        test_app.config["APP_ENV"] = original_env
