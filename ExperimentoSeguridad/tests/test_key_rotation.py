"""
Test: Cambia kid, mantiene públicas anteriores, ≤0.5% errores espurios bajo carga concurrente
"""
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from app.utils.key_manager import key_manager

def test_key_rotation_creates_new_kid(client, admin_token):
    """Test que rotación de claves crea nuevo kid"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Obtener kid actual
    current_kids = key_manager.get_all_kids()
    initial_count = len(current_kids)
    
    # Rotar claves
    response = client.post("/auth/rotate-keys", headers=headers)
    assert response.status_code == 200
    
    response_data = response.json()
    assert "new_kid" in response_data
    assert "active_kid" in response_data
    assert response_data["new_kid"] == response_data["active_kid"]
    
    # Verificar que se creó nueva clave
    new_kids = key_manager.get_all_kids()
    assert len(new_kids) == initial_count + 1
    assert response_data["new_kid"] in new_kids

def test_old_keys_remain_accessible_after_rotation(client, admin_token):
    """Test que claves anteriores siguen siendo accesibles después de rotación"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Obtener kid actual
    old_kid = key_manager.get_active_kid()
    
    # Rotar claves
    response = client.post("/auth/rotate-keys", headers=headers)
    assert response.status_code == 200
    
    new_kid = response.json()["new_kid"]
    assert new_kid != old_kid
    
    # Verificar que clave anterior sigue disponible
    try:
        old_public_key = key_manager.get_public_key_pem(old_kid)
        assert old_public_key is not None
    except Exception as e:
        pytest.fail(f"Clave anterior no disponible: {e}")
    
    # Verificar que nueva clave está disponible
    try:
        new_public_key = key_manager.get_public_key_pem(new_kid)
        assert new_public_key is not None
    except Exception as e:
        pytest.fail(f"Nueva clave no disponible: {e}")

def test_tokens_with_old_kid_still_work(client, admin_user_data):
    """Test que tokens firmados con kid anterior siguen funcionando"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Obtener kid actual
    old_kid = key_manager.get_active_kid()
    
    # Crear token con kid actual
    login_data = {
        "username": admin_user_data["email"],
        "password": admin_user_data["contrasena"]
    }
    response = client.post("/token", data=login_data)
    old_token = response.json()["access_token"]
    
    # Rotar claves
    headers = {"Authorization": f"Bearer {old_token}"}
    response = client.post("/auth/rotate-keys", headers=headers)
    assert response.status_code == 200
    
    # Token con kid anterior debería seguir funcionando
    response = client.get("/users/1", headers=headers)
    assert response.status_code == 200

def test_new_tokens_use_new_kid(client, admin_user_data):
    """Test que nuevos tokens usan el nuevo kid"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Login inicial
    login_data = {
        "username": admin_user_data["email"],
        "password": admin_user_data["contrasena"]
    }
    response = client.post("/token", data=login_data)
    old_token = response.json()["access_token"]
    
    # Rotar claves
    headers = {"Authorization": f"Bearer {old_token}"}
    response = client.post("/auth/rotate-keys", headers=headers)
    assert response.status_code == 200
    
    new_kid = response.json()["new_kid"]
    
    # Crear nuevo token (debería usar nuevo kid)
    response = client.post("/token", data=login_data)
    new_token = response.json()["access_token"]
    
    # Verificar que nuevo token usa nuevo kid
    import jwt as pyjwt
    unverified_header = pyjwt.get_unverified_header(new_token)
    assert unverified_header["kid"] == new_kid

def test_concurrent_requests_during_rotation(client, admin_user_data):
    """Test que requests concurrentes durante rotación tienen ≤0.5% errores espurios"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Login
    login_data = {
        "username": admin_user_data["email"],
        "password": admin_user_data["contrasena"]
    }
    response = client.post("/token", data=login_data)
    access_token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Función para hacer request
    def make_request():
        try:
            response = client.get("/users/1", headers=headers)
            return response.status_code == 200
        except Exception:
            return False
    
    # Hacer requests concurrentes durante rotación
    num_requests = 100
    errors = 0
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Iniciar requests concurrentes
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        
        # Rotar claves durante requests
        time.sleep(0.1)  # Pequeña pausa para que algunos requests empiecen
        response = client.post("/auth/rotate-keys", headers=headers)
        assert response.status_code == 200
        
        # Esperar a que terminen todos los requests
        for future in futures:
            if not future.result():
                errors += 1
    
    # Calcular porcentaje de errores
    error_rate = (errors / num_requests) * 100
    print(f"Error rate during key rotation: {error_rate:.2f}%")
    
    # Debe ser ≤0.5%
    assert error_rate <= 0.5, f"Error rate {error_rate:.2f}% exceeds 0.5% threshold"

def test_multiple_rotations_maintain_consistency(client, admin_user_data):
    """Test que múltiples rotaciones mantienen consistencia"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Login
    login_data = {
        "username": admin_user_data["email"],
        "password": admin_user_data["contrasena"]
    }
    response = client.post("/token", data=login_data)
    access_token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Hacer múltiples rotaciones
    kids_created = []
    for i in range(5):
        response = client.post("/auth/rotate-keys", headers=headers)
        assert response.status_code == 200
        
        new_kid = response.json()["new_kid"]
        kids_created.append(new_kid)
        
        # Verificar que todas las claves anteriores siguen disponibles
        for kid in kids_created:
            try:
                key_manager.get_public_key_pem(kid)
            except Exception as e:
                pytest.fail(f"Clave {kid} no disponible después de rotación {i+1}: {e}")
    
    # Verificar que se crearon 5 nuevas claves
    all_kids = key_manager.get_all_kids()
    assert len(all_kids) >= 6  # Al menos 6 claves (1 inicial + 5 rotaciones)

def test_rotation_preserves_jwks_endpoint(client, admin_token):
    """Test que endpoint JWKS mantiene todas las claves después de rotación"""
    # Obtener JWKS inicial
    response = client.get("/.well-known/jwks.json")
    assert response.status_code == 200
    initial_jwks = response.json()
    initial_keys_count = len(initial_jwks["keys"])
    
    # Rotar claves
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post("/auth/rotate-keys", headers=headers)
    assert response.status_code == 200
    
    # Obtener JWKS después de rotación
    response = client.get("/.well-known/jwks.json")
    assert response.status_code == 200
    new_jwks = response.json()
    new_keys_count = len(new_jwks["keys"])
    
    # Debe tener al menos una clave más
    assert new_keys_count >= initial_keys_count + 1
    
    # Todas las claves deben tener la estructura correcta
    for key in new_jwks["keys"]:
        assert "kty" in key
        assert "kid" in key
        assert "use" in key
        assert "alg" in key
        assert "n" in key
        assert "e" in key
        assert key["kty"] == "RSA"
        assert key["alg"] == "RS256"
        assert key["use"] == "sig"
