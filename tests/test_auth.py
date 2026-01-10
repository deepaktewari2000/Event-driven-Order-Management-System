import pytest
from fastapi.testclient import TestClient


class TestAuthentication:
    """Test authentication endpoints."""

    def test_register_user(self, client: TestClient):
        """Test user registration."""
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "full_name": "New User"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert data["role"] == "CUSTOMER"
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Test registration with existing email fails."""
        response = client.post(
            "/auth/register",
            json={
                "email": test_user.email,
                "password": "AnotherPass123!",
                "full_name": "Duplicate User"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_login_success(self, client: TestClient, test_user):
        """Test successful login."""
        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient, test_user):
        """Test login with wrong password fails."""
        response = client.post(
            "/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user fails."""
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "somepassword"
            }
        )
        assert response.status_code == 401

    def test_get_current_user(self, client: TestClient, test_user, auth_headers):
        """Test getting current user information."""
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["role"] == test_user.role.value

    def test_get_current_user_no_token(self, client: TestClient):
        """Test accessing protected endpoint without token fails."""
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test accessing protected endpoint with invalid token fails."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
