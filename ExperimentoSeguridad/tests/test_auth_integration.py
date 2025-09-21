"""
Integration tests for authentication and authorization.
"""
import pytest
import httpx
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestAuthentication:
    """Test authentication flows."""

    def test_login_success(self):
        """Test successful login."""
        # First create a user
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
            "role": "user"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201

        # Then login
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 401

    def test_get_user_without_auth(self):
        """Test getting user data without authentication."""
        response = client.get("/users/me")
        assert response.status_code == 401

    def test_get_user_with_auth(self):
        """Test getting user data with valid authentication."""
        # Create user
        user_data = {
            "email": "auth@example.com",
            "password": "testpassword123",
            "full_name": "Auth User",
            "role": "user"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201

        # Login
        login_data = {
            "username": "auth@example.com",
            "password": "testpassword123"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 200
        
        token = response.json()["access_token"]
        
        # Get user data
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == "auth@example.com"
        assert data["role"] == "user"

    def test_token_revocation(self):
        """Test token revocation."""
        # Create user
        user_data = {
            "email": "revoke@example.com",
            "password": "testpassword123",
            "full_name": "Revoke User",
            "role": "user"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201

        # Login
        login_data = {
            "username": "revoke@example.com",
            "password": "testpassword123"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 200
        
        token = response.json()["access_token"]
        
        # Verify token works
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 200

        # Revoke token
        response = client.post("/auth/revoke", headers=headers)
        assert response.status_code == 200

        # Verify token no longer works
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 401

    def test_revoke_other_user_token(self):
        """Test that users cannot revoke other users' tokens."""
        # Create two users
        user1_data = {
            "email": "user1@example.com",
            "password": "testpassword123",
            "full_name": "User 1",
            "role": "user"
        }
        response = client.post("/users/", json=user1_data)
        assert response.status_code == 201

        user2_data = {
            "email": "user2@example.com",
            "password": "testpassword123",
            "full_name": "User 2",
            "role": "user"
        }
        response = client.post("/users/", json=user2_data)
        assert response.status_code == 201

        # Login as user1
        login_data = {
            "username": "user1@example.com",
            "password": "testpassword123"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 200
        token1 = response.json()["access_token"]

        # Login as user2
        login_data = {
            "username": "user2@example.com",
            "password": "testpassword123"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 200
        token2 = response.json()["access_token"]

        # User1 tries to revoke user2's token (should fail)
        headers = {"Authorization": f"Bearer {token1}"}
        response = client.post("/auth/revoke", headers=headers, json={"token": token2})
        assert response.status_code == 403

    def test_token_refresh(self):
        """Test token refresh functionality."""
        # Create user
        user_data = {
            "email": "refresh@example.com",
            "password": "testpassword123",
            "full_name": "Refresh User",
            "role": "user"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201

        # Login
        login_data = {
            "username": "refresh@example.com",
            "password": "testpassword123"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 200
        
        token = response.json()["access_token"]
        
        # Refresh token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/auth/refresh", headers=headers)
        assert response.status_code == 200
        
        new_token = response.json()["access_token"]
        assert new_token != token

        # Verify new token works
        headers = {"Authorization": f"Bearer {new_token}"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 200

    def test_jwks_endpoint(self):
        """Test JWKS endpoint returns at least one key."""
        response = client.get("/.well-known/jwks.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "keys" in data
        assert len(data["keys"]) >= 1
        
        # Verify key structure
        key = data["keys"][0]
        assert "kid" in key
        assert "kty" in key
        assert "use" in key
        assert key["kty"] == "RSA"
        assert key["use"] == "sig"


class TestRBAC:
    """Test Role-Based Access Control."""

    def test_admin_can_create_users(self):
        """Test admin can create users."""
        # Create admin user
        admin_data = {
            "email": "admin@example.com",
            "password": "adminpassword123",
            "full_name": "Admin User",
            "role": "admin"
        }
        response = client.post("/users/", json=admin_data)
        assert response.status_code == 201

        # Login as admin
        login_data = {
            "username": "admin@example.com",
            "password": "adminpassword123"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 200
        
        admin_token = response.json()["access_token"]
        
        # Admin creates new user
        headers = {"Authorization": f"Bearer {admin_token}"}
        new_user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User",
            "role": "user"
        }
        response = client.post("/users/", json=new_user_data, headers=headers)
        assert response.status_code == 201

    def test_user_cannot_create_users(self):
        """Test regular user cannot create users."""
        # Create regular user
        user_data = {
            "email": "regular@example.com",
            "password": "userpassword123",
            "full_name": "Regular User",
            "role": "user"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201

        # Login as regular user
        login_data = {
            "username": "regular@example.com",
            "password": "userpassword123"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 200
        
        user_token = response.json()["access_token"]
        
        # Regular user tries to create new user (should fail)
        headers = {"Authorization": f"Bearer {user_token}"}
        new_user_data = {
            "email": "unauthorized@example.com",
            "password": "newpassword123",
            "full_name": "Unauthorized User",
            "role": "user"
        }
        response = client.post("/users/", json=new_user_data, headers=headers)
        assert response.status_code == 403

    def test_admin_can_view_blacklist(self):
        """Test admin can view token blacklist."""
        # Create admin user
        admin_data = {
            "email": "admin2@example.com",
            "password": "adminpassword123",
            "full_name": "Admin User 2",
            "role": "admin"
        }
        response = client.post("/users/", json=admin_data)
        assert response.status_code == 201

        # Login as admin
        login_data = {
            "username": "admin2@example.com",
            "password": "adminpassword123"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 200
        
        admin_token = response.json()["access_token"]
        
        # Admin views blacklist
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/auth/blacklist", headers=headers)
        assert response.status_code == 200

    def test_user_cannot_view_blacklist(self):
        """Test regular user cannot view blacklist."""
        # Create regular user
        user_data = {
            "email": "regular2@example.com",
            "password": "userpassword123",
            "full_name": "Regular User 2",
            "role": "user"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201

        # Login as regular user
        login_data = {
            "username": "regular2@example.com",
            "password": "userpassword123"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 200
        
        user_token = response.json()["access_token"]
        
        # Regular user tries to view blacklist (should fail)
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/auth/blacklist", headers=headers)
        assert response.status_code == 403


class TestMetrics:
    """Test metrics endpoint."""

    def test_metrics_endpoint(self):
        """Test metrics endpoint is accessible."""
        response = client.get("/metrics")
        assert response.status_code == 200
        
        # Check that response contains Prometheus metrics
        content = response.text
        assert "jwt_validation_seconds" in content
        assert "jwt_validation_failures_total" in content
        assert "jwt_validation_success_total" in content

    def test_health_endpoint(self):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
