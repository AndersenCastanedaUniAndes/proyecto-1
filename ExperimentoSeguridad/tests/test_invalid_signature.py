"""
Test: Token con firma inválida retorna 401
"""
import pytest
import jwt as pyjwt
from datetime import datetime, timedelta
from app.utils.key_manager import key_manager

def test_invalid_signature_returns_401(client, admin_user_data):
    """Test que token con firma inválida retorna 401"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Crear token con firma inválida
    payload = {
        "sub": admin_user_data["email"],
        "role": admin_user_data["rol"],
        "jti": "test_jti",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iss": "experimento-seguridad",
        "aud": "api-users"
    }
    
    # Firmar con clave incorrecta (usar clave pública como privada)
    kid = key_manager.get_active_kid()
    public_key_pem = key_manager.get_public_key_pem(kid)
    
    # Esto debería fallar o crear un token inválido
    try:
        invalid_token = pyjwt.encode(
            payload,
            public_key_pem,  # Clave incorrecta
            algorithm="RS256",
            headers={"kid": kid, "typ": "JWT", "alg": "RS256"}
        )
    except Exception:
        # Si falla la creación, crear un token con datos corruptos
        invalid_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6ImtleS0xIn0.eyJzdWIiOiJhZG1pbkB0ZXN0LmNvbSIsInJvbGUiOiJhZG1pbiIsImp0aSI6InRlc3RfanRpIiwiaWF0IjoxNjQwOTk1MjAwLCJleHAiOjE2NDEwMTMyMDAsImlzcyI6ImV4cGVyaW1lbnRvLXNlZ3VyaWRhZCIsImF1ZCI6ImFwaS11c2VycyJ9.invalid_signature"
    
    # Intentar usar token con firma inválida
    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = client.get("/users/1", headers=headers)
    assert response.status_code == 401

def test_wrong_kid_returns_401(client, admin_user_data):
    """Test que token con kid incorrecto retorna 401"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Crear token con kid inexistente
    payload = {
        "sub": admin_user_data["email"],
        "role": admin_user_data["rol"],
        "jti": "test_jti",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iss": "experimento-seguridad",
        "aud": "api-users"
    }
    
    # Usar kid inexistente
    invalid_token = pyjwt.encode(
        payload,
        "invalid_key",
        algorithm="RS256",
        headers={"kid": "invalid_kid", "typ": "JWT", "alg": "RS256"}
    )
    
    # Intentar usar token con kid incorrecto
    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = client.get("/users/1", headers=headers)
    assert response.status_code == 401

def test_malformed_token_returns_401(client):
    """Test que token malformado retorna 401"""
    # Tokens malformados
    malformed_tokens = [
        "not.a.token",
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9",
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.invalid",
        "invalid.token.here",
        "",
        "Bearer",
        "Bearer ",
    ]
    
    for token in malformed_tokens:
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/1", headers=headers)
        assert response.status_code == 401

def test_token_without_kid_returns_401(client, admin_user_data):
    """Test que token sin kid retorna 401"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Crear token sin kid en header
    payload = {
        "sub": admin_user_data["email"],
        "role": admin_user_data["rol"],
        "jti": "test_jti",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iss": "experimento-seguridad",
        "aud": "api-users"
    }
    
    # Firmar sin kid en header
    kid = key_manager.get_active_kid()
    private_key_pem = key_manager.get_private_key_pem(kid)
    
    token_without_kid = pyjwt.encode(
        payload,
        private_key_pem,
        algorithm="RS256",
        headers={"typ": "JWT", "alg": "RS256"}  # Sin kid
    )
    
    # Intentar usar token sin kid
    headers = {"Authorization": f"Bearer {token_without_kid}"}
    response = client.get("/users/1", headers=headers)
    assert response.status_code == 401
