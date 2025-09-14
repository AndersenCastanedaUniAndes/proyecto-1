"""
Test: GET permitido para admin/user, DELETE solo admin
"""
import pytest

def test_admin_can_read_users(client, admin_token, regular_user_data):
    """Test que admin puede leer usuarios"""
    # Crear usuario regular
    response = client.post("/users/", json=regular_user_data)
    assert response.status_code == 200
    user_id = response.json()["usuario_id"]
    
    # Admin lee el usuario
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == regular_user_data["email"]

def test_user_can_read_users(client, user_token, admin_user_data):
    """Test que usuario regular puede leer usuarios"""
    # Crear usuario admin
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    user_id = response.json()["usuario_id"]
    
    # Usuario regular lee el usuario
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == admin_user_data["email"]

def test_admin_can_delete_users(client, admin_token, regular_user_data):
    """Test que admin puede eliminar usuarios"""
    # Crear usuario regular
    response = client.post("/users/", json=regular_user_data)
    assert response.status_code == 200
    user_id = response.json()["usuario_id"]
    
    # Admin elimina el usuario
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200
    assert "eliminado" in response.json()["message"].lower()

def test_user_cannot_delete_users(client, user_token, admin_user_data):
    """Test que usuario regular NO puede eliminar usuarios"""
    # Crear usuario admin
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    user_id = response.json()["usuario_id"]
    
    # Usuario regular intenta eliminar
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.delete(f"/users/{user_id}", headers=headers)
    assert response.status_code == 403
    assert "permisos" in response.json()["detail"].lower()

def test_admin_can_rotate_keys(client, admin_token):
    """Test que admin puede rotar claves"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post("/auth/rotate-keys", headers=headers)
    assert response.status_code == 200
    assert "new_kid" in response.json()

def test_user_cannot_rotate_keys(client, user_token):
    """Test que usuario regular NO puede rotar claves"""
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post("/auth/rotate-keys", headers=headers)
    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()

def test_admin_can_view_blacklist(client, admin_token):
    """Test que admin puede ver la blacklist"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/auth/blacklist", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_user_cannot_view_blacklist(client, user_token):
    """Test que usuario regular NO puede ver la blacklist"""
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/auth/blacklist", headers=headers)
    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()

def test_unauthorized_access_returns_401(client, regular_user_data):
    """Test que acceso sin token retorna 401"""
    # Crear usuario
    response = client.post("/users/", json=regular_user_data)
    assert response.status_code == 200
    user_id = response.json()["usuario_id"]
    
    # Intentar acceder sin token
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 401

def test_invalid_token_returns_401(client, regular_user_data):
    """Test que token inválido retorna 401"""
    # Crear usuario
    response = client.post("/users/", json=regular_user_data)
    assert response.status_code == 200
    user_id = response.json()["usuario_id"]
    
    # Intentar acceder con token inválido
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 401
