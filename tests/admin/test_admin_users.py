"""Tests for admin user management endpoints."""

import pytest
from app.models import User
from app.models.enums import Role

@pytest.fixture
def admin_user(session):
    """Create admin user."""
    session.query(User).delete()
    user = User(
        email="admin@example.com",
        full_name="Admin User",
        password_hash="hash",
        role=Role.ADMIN,
        is_active=True,
    )
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def customer_users(session):
    """Create multiple customer users."""
    users = [
        User(email=f"customer{i}@example.com", full_name=f"Customer {i}", password_hash="hash", role=Role.CUSTOMER, is_active=True)
        for i in range(3)
    ]
    session.add_all(users)
    session.commit()
    return users

class TestListUsers:
    def test_list_users_success(self, test_app, admin_user, customer_users, auth_header):
        """Should list all users with pagination."""
        with test_app.test_client() as client:
            response = client.get(
                "/api/v1/admin/users",
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()
            assert "data" in data
            assert "total" in data
            assert data["total"] >= 4  # admin + 3 customers

    def test_list_users_filter_by_role(self, test_app, admin_user, customer_users, auth_header):
        """Should filter users by role."""
        with test_app.test_client() as client:
            response = client.get(
                "/api/v1/admin/users?role=CUSTOMER",
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert all(user["role"] == "CUSTOMER" for user in data)

    def test_list_users_search(self, test_app, admin_user, customer_users, auth_header):
        """Should search users by email or name."""
        with test_app.test_client() as client:
            response = client.get(
                "/api/v1/admin/users?q=customer1",
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert len(data) >= 1
            assert any("customer1" in user["email"] for user in data)

    def test_list_users_requires_admin(self, test_app, customer_users, auth_header):
        """Should require admin/manager role."""
        with test_app.test_client() as client:
            response = client.get(
                "/api/v1/admin/users",
                headers=auth_header(customer_users[0]),
            )
            assert response.status_code == 403


class TestGetUser:
    """Tests for GET /api/v1/admin/users/{user_id}"""

    def test_get_user_success(self, test_app, admin_user, customer_users, auth_header):
        """Should get user details."""
        target_user = customer_users[0]
        with test_app.test_client() as client:
            response = client.get(
                f"/api/v1/admin/users/{target_user.id}",
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["id"] == str(target_user.id)
            assert data["email"] == target_user.email

    def test_get_user_not_found(self, test_app, admin_user, auth_header):
        """Should return 404 for non-existent user."""
        import uuid
        with test_app.test_client() as client:
            response = client.get(
                f"/api/v1/admin/users/{uuid.uuid4()}",
                headers=auth_header(admin_user),
            )
            assert response.status_code == 404


class TestUpdateUser:
    """Tests for PATCH /api/v1/admin/users/{user_id}"""

    def test_update_user_role(self, test_app, admin_user, customer_users, auth_header, session):
        """Should update user role."""
        target_user = customer_users[0]
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/users/{target_user.id}",
                json={"role": "EMPLOYEE"},
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["role"] == "EMPLOYEE"
            
            # Verify in DB
            session.refresh(target_user)
            assert target_user.role == Role.EMPLOYEE

    def test_update_user_deactivate(self, test_app, admin_user, customer_users, auth_header, session):
        """Should deactivate user."""
        target_user = customer_users[0]
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/users/{target_user.id}",
                json={"is_active": False},
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["is_active"] is False

    def test_cannot_modify_own_role(self, test_app, admin_user, auth_header):
        """Should prevent admin from changing their own role."""
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/users/{admin_user.id}",
                json={"role": "CUSTOMER"},
                headers=auth_header(admin_user),
            )
            assert response.status_code == 403
            assert "CANNOT_MODIFY_SELF_ROLE" in response.get_json()["error"]["code"]


class TestToggleUser:
    """Tests for PATCH /api/v1/admin/users/{user_id}/toggle"""

    def test_toggle_user_activate(self, test_app, admin_user, customer_users, auth_header, session):
        """Should toggle user active status."""
        target_user = customer_users[0]
        target_user.is_active = False
        session.commit()

        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/users/{target_user.id}/toggle?active=true",
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["is_active"] is True

    def test_cannot_deactivate_self(self, test_app, admin_user, auth_header):
        """Should prevent admin from deactivating themselves."""
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/users/{admin_user.id}/toggle?active=false",
                headers=auth_header(admin_user),
            )
            assert response.status_code == 403
            assert "CANNOT_DEACTIVATE_SELF" in response.get_json()["error"]["code"]

    def test_toggle_missing_param(self, test_app, admin_user, customer_users, auth_header):
        """Should require active query parameter."""
        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/users/{customer_users[0].id}/toggle",
                headers=auth_header(admin_user),
            )
            assert response.status_code == 400
