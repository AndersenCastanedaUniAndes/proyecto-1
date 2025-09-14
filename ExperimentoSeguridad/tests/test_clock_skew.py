"""
Test: Tolerancia a clock skew ±60s
"""
import pytest
import jwt as pyjwt
from datetime import datetime, timedelta
from app.utils.key_manager import key_manager

def test_token_with_clock_skew_plus_60s_works(client, admin_user_data):
    """Test que token con clock skew +60s funciona"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Crear token con iat 60 segundos en el futuro (clock skew)
    now = datetime.utcnow()
    payload = {
        "sub": admin_user_data["email"],
        "role": admin_user_data["rol"],
        "jti": "test_jti_skew_plus",
        "iat": now + timedelta(seconds=60),  # +60s clock skew
        "exp": now + timedelta(minutes=30),
        "iss": "experimento-seguridad",
        "aud": "api-users"
    }
    
    # Firmar token
    kid = key_manager.get_active_kid()
    private_key_pem = key_manager.get_private_key_pem(kid)
    
    token_with_skew = pyjwt.encode(
        payload,
        private_key_pem,
        algorithm="RS256",
        headers={"kid": kid, "typ": "JWT", "alg": "RS256"}
    )
    
    # Token debería funcionar debido a leeway=60s
    headers = {"Authorization": f"Bearer {token_with_skew}"}
    response = client.get("/users/1", headers=headers)
    assert response.status_code == 200

def test_token_with_clock_skew_minus_60s_works(client, admin_user_data):
    """Test que token con clock skew -60s funciona"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Crear token con iat 60 segundos en el pasado (clock skew)
    now = datetime.utcnow()
    payload = {
        "sub": admin_user_data["email"],
        "role": admin_user_data["rol"],
        "jti": "test_jti_skew_minus",
        "iat": now - timedelta(seconds=60),  # -60s clock skew
        "exp": now + timedelta(minutes=30),
        "iss": "experimento-seguridad",
        "aud": "api-users"
    }
    
    # Firmar token
    kid = key_manager.get_active_kid()
    private_key_pem = key_manager.get_private_key_pem(kid)
    
    token_with_skew = pyjwt.encode(
        payload,
        private_key_pem,
        algorithm="RS256",
        headers={"kid": kid, "typ": "JWT", "alg": "RS256"}
    )
    
    # Token debería funcionar debido a leeway=60s
    headers = {"Authorization": f"Bearer {token_with_skew}"}
    response = client.get("/users/1", headers=headers)
    assert response.status_code == 200

def test_token_with_clock_skew_plus_61s_fails(client, admin_user_data):
    """Test que token con clock skew +61s falla (fuera de tolerancia)"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Crear token con iat 61 segundos en el futuro (fuera de tolerancia)
    now = datetime.utcnow()
    payload = {
        "sub": admin_user_data["email"],
        "role": admin_user_data["rol"],
        "jti": "test_jti_skew_plus_61",
        "iat": now + timedelta(seconds=61),  # +61s clock skew (fuera de tolerancia)
        "exp": now + timedelta(minutes=30),
        "iss": "experimento-seguridad",
        "aud": "api-users"
    }
    
    # Firmar token
    kid = key_manager.get_active_kid()
    private_key_pem = key_manager.get_private_key_pem(kid)
    
    token_with_skew = pyjwt.encode(
        payload,
        private_key_pem,
        algorithm="RS256",
        headers={"kid": kid, "typ": "JWT", "alg": "RS256"}
    )
    
    # Token debería fallar por estar fuera de tolerancia
    headers = {"Authorization": f"Bearer {token_with_skew}"}
    response = client.get("/users/1", headers=headers)
    assert response.status_code == 401

def test_token_with_clock_skew_minus_61s_fails(client, admin_user_data):
    """Test que token con clock skew -61s falla (fuera de tolerancia)"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Crear token con iat 61 segundos en el pasado (fuera de tolerancia)
    now = datetime.utcnow()
    payload = {
        "sub": admin_user_data["email"],
        "role": admin_user_data["rol"],
        "jti": "test_jti_skew_minus_61",
        "iat": now - timedelta(seconds=61),  # -61s clock skew (fuera de tolerancia)
        "exp": now + timedelta(minutes=30),
        "iss": "experimento-seguridad",
        "aud": "api-users"
    }
    
    # Firmar token
    kid = key_manager.get_active_kid()
    private_key_pem = key_manager.get_private_key_pem(kid)
    
    token_with_skew = pyjwt.encode(
        payload,
        private_key_pem,
        algorithm="RS256",
        headers={"kid": kid, "typ": "JWT", "alg": "RS256"}
    )
    
    # Token debería fallar por estar fuera de tolerancia
    headers = {"Authorization": f"Bearer {token_with_skew}"}
    response = client.get("/users/1", headers=headers)
    assert response.status_code == 401

def test_expired_token_with_clock_skew_fails(client, admin_user_data):
    """Test que token expirado con clock skew falla"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Crear token expirado con clock skew
    now = datetime.utcnow()
    payload = {
        "sub": admin_user_data["email"],
        "role": admin_user_data["rol"],
        "jti": "test_jti_expired_skew",
        "iat": now - timedelta(minutes=1),
        "exp": now - timedelta(seconds=30),  # Expirado hace 30s
        "iss": "experimento-seguridad",
        "aud": "api-users"
    }
    
    # Firmar token
    kid = key_manager.get_active_kid()
    private_key_pem = key_manager.get_private_key_pem(kid)
    
    expired_token = pyjwt.encode(
        payload,
        private_key_pem,
        algorithm="RS256",
        headers={"kid": kid, "typ": "JWT", "alg": "RS256"}
    )
    
    # Token expirado debería fallar incluso con clock skew
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/users/1", headers=headers)
    assert response.status_code == 401
