"""Tests for admin branch management endpoints."""

import pytest
from app.models import User, Branch, Inventory, Product, Category
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


class TestBranchManagement:
    """Tests for branch CRUD"""

    def test_create_branch(self, test_app, admin_user, auth_header):
        """Should create a new branch."""
        with test_app.test_client() as client:
            response = client.post(
                "/api/v1/admin/branches",
                json={"name": "New Branch", "address": "456 New St"},
                headers=auth_header(admin_user),
            )
            assert response.status_code == 201
            data = response.get_json()["data"]
            assert data["name"] == "New Branch"
            assert data["address"] == "456 New St"

    def test_update_branch(self, test_app, admin_user, auth_header, session):
        """Should update branch details."""
        branch = Branch(name="Old Branch", address="Old Address", is_active=True)
        session.add(branch)
        session.commit()

        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/branches/{branch.id}",
                json={"name": "Updated Branch", "address": "Old Address"},
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["name"] == "Updated Branch"

    def test_toggle_branch(self, test_app, admin_user, auth_header, session):
        """Should toggle branch active status."""
        branch = Branch(name="Test", address="Test St", is_active=True)
        session.add(branch)
        session.commit()

        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/branches/{branch.id}/toggle?active=false",
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["is_active"] is False


class TestInventoryManagement:
    """Tests for inventory management"""

    def test_update_inventory(self, test_app, admin_user, auth_header, session):
        """Should update inventory quantity."""
        category = Category(name="Cat", description="Test")
        session.add(category)
        session.flush()
        product = Product(name="Test", sku="SKU1", price="10.00", category_id=category.id)
        branch = Branch(name="Branch", address="Addr", is_active=True)
        session.add_all([product, branch])
        session.flush()
        inventory = Inventory(product_id=product.id, branch_id=branch.id, available_quantity=10)
        session.add(inventory)
        session.commit()

        with test_app.test_client() as client:
            response = client.put(
                f"/api/v1/admin/inventory/{inventory.id}",
                json={"available_quantity": 50, "reserved_quantity": 0},
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["available_quantity"] == 50
