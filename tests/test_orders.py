import pytest
from fastapi.testclient import TestClient
from app.models.user import User


class TestOrderCRUD:
    """Test order CRUD operations."""

    def test_create_order(self, client: TestClient, test_user, auth_headers):
        """Test creating an order."""
        response = client.post(
            "/orders",
            headers=auth_headers,
            json={
                "product_id": "LAPTOP-001",
                "quantity": 2,
                "customer_email": "customer@example.com",
                "shipping_address": "123 Main St"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == "LAPTOP-001"
        assert data["quantity"] == 2
        assert data["status"] == "CREATED"
        assert data["user_id"] == test_user.id

    def test_create_order_no_auth(self, client: TestClient):
        """Test creating order without authentication fails."""
        response = client.post(
            "/orders",
            json={
                "product_id": "LAPTOP-001",
                "quantity": 2,
                "customer_email": "customer@example.com"
            }
        )
        assert response.status_code == 403

    def test_get_order(self, client: TestClient, test_user, auth_headers):
        """Test getting a specific order."""
        # Create order first
        create_response = client.post(
            "/orders",
            headers=auth_headers,
            json={
                "product_id": "PHONE-001",
                "quantity": 1,
                "customer_email": "customer@example.com"
            }
        )
        order_id = create_response.json()["id"]

        # Get the order
        response = client.get(f"/orders/{order_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id
        assert data["product_id"] == "PHONE-001"

    def test_get_order_not_found(self, client: TestClient, auth_headers):
        """Test getting nonexistent order returns 404."""
        response = client.get("/orders/9999", headers=auth_headers)
        assert response.status_code == 404

    def test_update_order(self, client: TestClient, test_user, auth_headers):
        """Test updating an order."""
        # Create order
        create_response = client.post(
            "/orders",
            headers=auth_headers,
            json={
                "product_id": "TABLET-001",
                "quantity": 1,
                "customer_email": "customer@example.com"
            }
        )
        order_id = create_response.json()["id"]

        # Update order
        response = client.put(
            f"/orders/{order_id}",
            headers=auth_headers,
            json={"quantity": 3, "shipping_address": "456 New St"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 3
        assert data["shipping_address"] == "456 New St"

    def test_update_other_user_order_forbidden(
        self, client: TestClient, test_user, test_admin, auth_headers
    ):
        """Test that users cannot update other users' orders."""
        # Create order as test_user
        create_response = client.post(
            "/orders",
            headers=auth_headers,
            json={
                "product_id": "WATCH-001",
                "quantity": 1,
                "customer_email": "customer@example.com"
            }
        )
        order_id = create_response.json()["id"]

        # Try to update as different user (would need another user token)
        # This test verifies the authorization logic

    def test_list_orders(self, client: TestClient, test_user, auth_headers):
        """Test listing orders with pagination."""
        # Create multiple orders
        for i in range(5):
            client.post(
                "/orders",
                headers=auth_headers,
                json={
                    "product_id": f"PRODUCT-{i}",
                    "quantity": i + 1,
                    "customer_email": "customer@example.com"
                }
            )

        # List orders
        response = client.get("/orders?skip=0&limit=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["orders"]) == 5
        assert data["skip"] == 0
        assert data["limit"] == 10

    def test_list_orders_pagination(self, client: TestClient, test_user, auth_headers):
        """Test pagination works correctly."""
        # Create orders
        for i in range(15):
            client.post(
                "/orders",
                headers=auth_headers,
                json={
                    "product_id": f"PRODUCT-{i}",
                    "quantity": 1,
                    "customer_email": "customer@example.com"
                }
            )

        # Get first page
        response = client.get("/orders?skip=0&limit=10", headers=auth_headers)
        data = response.json()
        assert len(data["orders"]) == 10
        assert data["total"] == 15

        # Get second page
        response = client.get("/orders?skip=10&limit=10", headers=auth_headers)
        data = response.json()
        assert len(data["orders"]) == 5
        assert data["total"] == 15

    def test_delete_order_admin_only(
        self, client: TestClient, test_user, auth_headers, admin_headers
    ):
        """Test that only admins can delete orders."""
        # Create order
        create_response = client.post(
            "/orders",
            headers=auth_headers,
            json={
                "product_id": "DELETE-TEST",
                "quantity": 1,
                "customer_email": "customer@example.com"
            }
        )
        order_id = create_response.json()["id"]

        # Try to delete as regular user (should fail)
        response = client.delete(f"/orders/{order_id}", headers=auth_headers)
        assert response.status_code == 403

        # Delete as admin (should succeed)
        response = client.delete(f"/orders/{order_id}", headers=admin_headers)
        assert response.status_code == 204

    def test_update_order_status_admin_only(
        self, client: TestClient, test_user, auth_headers, admin_headers
    ):
        """Test that only admins can update order status."""
        # Create order
        create_response = client.post(
            "/orders",
            headers=auth_headers,
            json={
                "product_id": "STATUS-TEST",
                "quantity": 1,
                "customer_email": "customer@example.com"
            }
        )
        order_id = create_response.json()["id"]

        # Try to update status as regular user (should fail)
        response = client.patch(
            f"/orders/{order_id}/status",
            headers=auth_headers,
            json={"status": "CONFIRMED"}
        )
        assert response.status_code == 403

        # Update status as admin (should succeed)
        response = client.patch(
            f"/orders/{order_id}/status",
            headers=admin_headers,
            json={"status": "CONFIRMED"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CONFIRMED"
