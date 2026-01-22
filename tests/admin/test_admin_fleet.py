import pytest
from app.models.enums import Role

def test_admin_fleet_status(test_app, auth_header, monkeypatch, create_user_with_role):
    """GET /api/v1/admin/fleet/status returns fleet status for admin/manager only (אמיתי)."""

    admin = create_user_with_role(role=Role.ADMIN)
    with test_app.test_client() as client:
        response = client.get(
            "/api/v1/admin/fleet/status",
            headers=auth_header(admin),
        )
        assert response.status_code == 200
        data = response.get_json()["data"]
        # Check for expected keys and types
        assert "drivers_online" in data
        assert "vehicles_available" in data
        assert isinstance(data["drivers"], list)
        assert isinstance(data["vehicles"], list)
        # Optionally, check a sample driver/vehicle structure
        if data["drivers"]:
            assert "id" in data["drivers"][0]
            assert "name" in data["drivers"][0]
            assert "online" in data["drivers"][0]
        if data["vehicles"]:
            assert "id" in data["vehicles"][0]
            assert "type" in data["vehicles"][0]
            assert "available" in data["vehicles"][0]

    # forbidden for non-manager/admin
    employee = create_user_with_role(role=Role.EMPLOYEE)
    with test_app.test_client() as client:
        response = client.get(
            "/api/v1/admin/fleet/status",
            headers=auth_header(employee),
        )
        assert response.status_code == 403
