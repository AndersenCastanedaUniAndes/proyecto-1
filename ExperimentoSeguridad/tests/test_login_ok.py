"""
Test: Tokens válidos con kid, role, jti, iss, aud, exp
"""
import pytest
import jwt as pyjwt
from datetime import datetime, timedelta

def test_login_creates_valid_token(client, admin_user_data):
    """Test que el login crea un token válido con todos los claims requeridos"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Login
    login_data = {
        "username": admin_user_data["email"],
        "password": admin_user_data["contrasena"]
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    access_token = token_data["access_token"]
    
    # Verificar estructura del token
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert "expires_in" in token_data
    
    # Decodificar token sin verificación para inspeccionar claims
    unverified_payload = pyjwt.decode(access_token, options={"verify_signature": False})
    
    # Verificar claims requeridos
    assert "sub" in unverified_payload  # Subject (email)
    assert "role" in unverified_payload  # Rol del usuario
    assert "jti" in unverified_payload  # JWT ID
    assert "iat" in unverified_payload  # Issued at
    assert "exp" in unverified_payload  # Expiration
    assert "iss" in unverified_payload  # Issuer
    assert "aud" in unverified_payload  # Audience
    
    # Verificar valores específicos
    assert unverified_payload["sub"] == admin_user_data["email"]
    assert unverified_payload["role"] == admin_user_data["rol"]
    assert unverified_payload["iss"] == "experimento-seguridad"
    assert unverified_payload["aud"] == "api-users"
    
    # Verificar que exp está en el futuro
    exp_timestamp = unverified_payload["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    assert exp_datetime > datetime.utcnow()

def test_token_has_correct_header_kid(client, admin_user_data):
    """Test que el token tiene el header kid correcto"""
    # Crear usuario y login
    client.post("/users/", json=admin_user_data)
    login_data = {
        "username": admin_user_data["email"],
        "password": admin_user_data["contrasena"]
    }
    response = client.post("/token", data=login_data)
    access_token = response.json()["access_token"]
    
    # Decodificar header
    unverified_header = pyjwt.get_unverified_header(access_token)
    
    # Verificar header
    assert "kid" in unverified_header
    assert "typ" in unverified_header
    assert "alg" in unverified_header
    assert unverified_header["typ"] == "JWT"
    assert unverified_header["alg"] == "RS256"
    assert unverified_header["kid"] is not None

def test_refresh_token_creates_new_access_token(client, admin_user_data):
    """Test que el refresh token crea un nuevo access token válido"""
    # Crear usuario y login
    client.post("/users/", json=admin_user_data)
    login_data = {
        "username": admin_user_data["email"],
        "password": admin_user_data["contrasena"]
    }
    response = client.post("/token", data=login_data)
    token_data = response.json()
    refresh_token = token_data["refresh_token"]
    
    # Usar refresh token
    refresh_data = {"refresh_token": refresh_token}
    response = client.post("/auth/refresh", json=refresh_data)
    assert response.status_code == 200
    
    new_token_data = response.json()
    new_access_token = new_token_data["access_token"]
    
    # Verificar que es un token válido
    unverified_payload = pyjwt.decode(new_access_token, options={"verify_signature": False})
    assert "sub" in unverified_payload
    assert "role" in unverified_payload
    assert "jti" in unverified_payload
    assert unverified_payload["sub"] == admin_user_data["email"]
    assert unverified_payload["role"] == admin_user_data["rol"]

def test_token_verification_with_rs256(client, admin_user_data):
    """Test que el token se puede verificar correctamente con RS256"""
    # Crear usuario y login
    client.post("/users/", json=admin_user_data)
    login_data = {
        "username": admin_user_data["email"],
        "password": admin_user_data["contrasena"]
    }
    response = client.post("/token", data=login_data)
    access_token = response.json()["access_token"]
    
    # Obtener kid del token
    unverified_header = pyjwt.get_unverified_header(access_token)
    kid = unverified_header["kid"]
    
    # Obtener clave pública
    from app.utils.key_manager import key_manager
    public_key_pem = key_manager.get_public_key_pem(kid)
    
    # Verificar token con clave pública
    payload = pyjwt.decode(
        access_token,
        public_key_pem,
        algorithms=["RS256"],
        issuer="experimento-seguridad",
        audience="api-users"
    )
    
    # Verificar payload
    assert payload["sub"] == admin_user_data["email"]
    assert payload["role"] == admin_user_data["rol"]
    assert "jti" in payload
