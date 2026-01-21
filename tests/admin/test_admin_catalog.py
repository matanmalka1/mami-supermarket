"""Tests for admin catalog management endpoints."""

import pytest
from app.models import User, Category, Product
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


class TestCategoryManagement:
    """Tests for category CRUD"""

    def test_create_category(self, test_app, admin_user, auth_header):
        """Should create a new category."""
        with test_app.test_client() as client:
            response = client.post(
                "/api/v1/admin/categories",
                json={"name": "New Category", "description": "Test category"},
                headers=auth_header(admin_user),
            )
            assert response.status_code == 201
            data = response.get_json()["data"]
            assert data["name"] == "New Category"

    def test_update_category(self, test_app, admin_user, auth_header, session):
        """Should update category details."""
        category = Category(name="Old Name", description="Old desc")
        session.add(category)
        session.commit()

        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/categories/{category.id}",
                json={"name": "Updated Name", "description": "Updated desc"},
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["name"] == "Updated Name"

    def test_toggle_category(self, test_app, admin_user, auth_header, session):
        """Should toggle category active status."""
        category = Category(name="Test", description="Test", is_active=True)
        session.add(category)
        session.commit()

        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/categories/{category.id}/toggle?active=false",
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["is_active"] is False


class TestProductManagement:
    """Tests for product CRUD"""

    def test_create_product(self, test_app, admin_user, auth_header, session):
        """Should create a new product."""
        category = Category(name="Test Cat", description="Test")
        session.add(category)
        session.commit()

        with test_app.test_client() as client:
            response = client.post(
                "/api/v1/admin/products",
                json={
                    "name": "New Product",
                    "sku": "SKU123",
                    "price": 99.99,
                    "category_id": str(category.id),
                    "description": "Test product",
                },
                headers=auth_header(admin_user),
            )
            assert response.status_code == 201
            data = response.get_json()["data"]
            assert data["name"] == "New Product"
            assert data["sku"] == "SKU123"

    def test_update_product(self, test_app, admin_user, auth_header, session):
        """Should update product details."""
        category = Category(name="Cat", description="Test")
        session.add(category)
        session.flush()
        product = Product(
            name="Old Product",
            sku="OLD123",
            price="50.00",
            category_id=category.id,
        )
        session.add(product)
        session.commit()

        with test_app.test_client() as client:
            response = client.patch(
                f"/api/v1/admin/products/{product.id}",
                json={"name": "Updated Product", "price": 75.50},
                headers=auth_header(admin_user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["name"] == "Updated Product"
