"""Tests for address update endpoint."""

import pytest
from app.models import User
from app.models.enums import Role
from tests.profile_fixtures import customer_user, customer_with_addresses


class TestUpdateAddress:
    """Tests for PUT /api/v1/me/addresses/:id"""

    def test_update_address_success(self, test_app, customer_with_addresses, auth_header):
        """Should update an existing address."""
        user, addresses = customer_with_addresses
        address_id = addresses[0].id
        with test_app.test_client() as client:
            response = client.put(
                f"/api/v1/me/addresses/{address_id}",
                json={
                    "city": "Updated City",
                    "postal_code": "00000",
                },
                headers=auth_header(user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["city"] == "Updated City"
            assert data["postal_code"] == "00000"
            # Other fields unchanged
            assert data["address_line"] == addresses[0].address_line

    def test_update_address_not_found(self, test_app, customer_user, auth_header, session):
        """Should return 404 if address doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        with test_app.test_client() as client:
            response = client.put(
                f"/api/v1/me/addresses/{fake_id}",
                json={"city": "New City"},
                headers=auth_header(customer_user),
            )
            assert response.status_code == 404

    def test_update_other_user_address(self, test_app, customer_with_addresses, session, auth_header):
        """Should return 404 when trying to update another user's address."""
        user, addresses = customer_with_addresses
        # Create another user
        other_user = User(
            email="other@example.com",
            full_name="Other User",
            password_hash="hash",
            role=Role.CUSTOMER,
        )
        session.add(other_user)
        session.commit()

        address_id = addresses[0].id
        with test_app.test_client() as client:
            response = client.put(
                f"/api/v1/me/addresses/{address_id}",
                json={"city": "Hacked"},
                headers=auth_header(other_user),
            )
            assert response.status_code == 404

    def test_update_address_no_changes(self, test_app, customer_with_addresses, auth_header):
        """Should return unchanged address if no fields provided."""
        user, addresses = customer_with_addresses
        address_id = addresses[0].id
        with test_app.test_client() as client:
            response = client.put(
                f"/api/v1/me/addresses/{address_id}",
                json={},
                headers=auth_header(user),
            )
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["city"] == addresses[0].city
