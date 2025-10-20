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
