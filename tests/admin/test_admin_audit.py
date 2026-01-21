"""Tests for admin audit endpoints."""

import pytest
from app.models import User, Audit
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


class TestAuditEndpoints:
    """Tests for audit log retrieval"""

    def test_list_audit_logs(self, test_app, admin_user, auth_header, session):
        """Should list audit logs with pagination."""
        # Create audit records
        audit1 = Audit(
            entity_type="User",
            entity_id=admin_user.id,
            action="UPDATE",
            actor_user_id=admin_user.id,
            old_value={"email": "old@example.com"},
            new_value={"email": "new@example.com"},
        )
        audit2 = Audit(
            entity_type="Product",
            entity_id=admin_user.id,
            action="CREATE",
            actor_user_id=admin_user.id,
            new_value={"name": "New Product"},
        )
        session.add_all([audit1, audit2])
        session.commit()

        with test_app.test_client() as client:
            response = client.get(
                "/api/v1/admin/audit",
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()
            assert "data" in data
            assert "pagination" in data
            assert "total" in data["pagination"]
            assert isinstance(data["data"], list)

    def test_filter_by_entity_type(self, test_app, admin_user, auth_header, session):
        """Should filter audit logs by entity type."""
        audit = Audit(
            entity_type="User",
            entity_id=admin_user.id,
            action="UPDATE",
            actor_user_id=admin_user.id,
            old_value={"email": "old@example.com"},
            new_value={"email": "new@example.com"},
        )
        session.add(audit)
        session.commit()

        with test_app.test_client() as client:
            response = client.get(
                "/api/v1/admin/audit?entityType=User",
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            for record in data:
                assert record["entity_type"] == "User"

    def test_pagination_works(self, test_app, admin_user, auth_header, session):
        """Should respect pagination parameters."""
        for i in range(5):
            audit = Audit(
                entity_type="Test",
                entity_id=admin_user.id,
                action="CREATE",
                actor_user_id=admin_user.id,
                new_value={"index": i},
            )
            session.add(audit)
        session.commit()

        with test_app.test_client() as client:
            response = client.get(
                "/api/v1/admin/audit?limit=2&offset=0",
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["pagination"]["limit"] == 2
            assert len(data["data"]) <= 2

    def test_requires_admin_role(self, test_app, session, auth_header):
        """Should require admin role."""
        customer = User(
            email="customer@example.com",
            full_name="Customer",
            password_hash="hash",
            role=Role.CUSTOMER,
        )
        session.add(customer)
        session.commit()

        with test_app.test_client() as client:
            response = client.get(
                "/api/v1/admin/audit",
                headers=auth_header(customer),
            )
            assert response.status_code == 403
