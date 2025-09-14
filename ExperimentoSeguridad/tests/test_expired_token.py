"""
Test: Token expirado retorna 401
"""
import pytest
import jwt as pyjwt
from datetime import datetime, timedelta
from app.utils.key_manager import key_manager

def test_expired_token_returns_401(client, admin_user_data):
    """Test que token expirado retorna 401"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Crear token expirado manualmente
    expired_payload = {
        "sub": admin_user_data["email"],
        "role": admin_user_data["rol"],
        "jti": "test_jti",
        "iat": datetime.utcnow() - timedelta(hours=1),
        "exp": datetime.utcnow() - timedelta(minutes=1),  # Expirado hace 1 minuto
        "iss": "experimento-seguridad",
        "aud": "api-users"
    }
    
    # Firmar con clave privada
    kid = key_manager.get_active_kid()
    private_key_pem = key_manager.get_private_key_pem(kid)
    
    expired_token = pyjwt.encode(
        expired_payload,
        private_key_pem,
        algorithm="RS256",
        headers={"kid": kid, "typ": "JWT", "alg": "RS256"}
    )
    
    # Intentar usar token expirado
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/users/1", headers=headers)
    assert response.status_code == 401
    assert "expirado" in response.json()["detail"].lower()

def test_token_expires_after_ttl(client, admin_user_data):
    """Test que token expira después del TTL configurado"""
    # Crear usuario y login
    client.post("/users/", json=admin_user_data)
    login_data = {
        "username": admin_user_data["email"],
        "password": admin_user_data["contrasena"]
    }
    response = client.post("/token", data=login_data)
    access_token = response.json()["access_token"]
    
    # Decodificar para verificar exp
    unverified_payload = pyjwt.decode(access_token, options={"verify_signature": False})
    exp_timestamp = unverified_payload["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    
    # Verificar que exp está aproximadamente 30 minutos en el futuro
    expected_exp = datetime.utcnow() + timedelta(minutes=30)
    time_diff = abs((exp_datetime - expected_exp).total_seconds())
    assert time_diff < 60  # Diferencia menor a 1 minuto

def test_refresh_token_expires_after_ttl(client, admin_user_data):
    """Test que refresh token expira después del TTL configurado"""
    # Crear usuario y login
    client.post("/users/", json=admin_user_data)
    login_data = {
        "username": admin_user_data["email"],
        "password": admin_user_data["contrasena"]
    }
    response = client.post("/token", data=login_data)
    refresh_token = response.json()["refresh_token"]
    
    # Decodificar para verificar exp
    unverified_payload = pyjwt.decode(refresh_token, options={"verify_signature": False})
    exp_timestamp = unverified_payload["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    
    # Verificar que exp está aproximadamente 7 días en el futuro
    expected_exp = datetime.utcnow() + timedelta(days=7)
    time_diff = abs((exp_datetime - expected_exp).total_seconds())
    assert time_diff < 3600  # Diferencia menor a 1 hora
