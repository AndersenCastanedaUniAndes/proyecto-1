"""
Test: Simula Redis caído, usa fallback SQL, 0 accesos indebidos, métrica redis_down
"""
import pytest
from unittest.mock import patch, MagicMock
from app.utils.revocation_store import RevocationStore

def test_revocation_with_redis_down_uses_sql_fallback(client, admin_user_data, db_session):
    """Test que revocación funciona con Redis caído usando fallback SQL"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Login para obtener token
    login_data = {
        "username": admin_user_data["email"],
        "password": admin_user_data["contrasena"]
    }
    response = client.post("/token", data=login_data)
    access_token = response.json()["access_token"]
    
    # Simular Redis caído
    with patch('app.utils.revocation_store.redis.from_url') as mock_redis:
        # Configurar mock para simular Redis caído
        mock_redis_client = MagicMock()
        mock_redis_client.ping.side_effect = Exception("Redis connection failed")
        mock_redis.return_value = mock_redis_client
        
        # Crear nueva instancia de RevocationStore (simula Redis caído)
        revocation_store = RevocationStore()
        assert not revocation_store.redis_available
        
        # Verificar que token funciona antes de revocar
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/users/1", headers=headers)
        assert response.status_code == 200
        
        # Revocar token (debería usar fallback SQL)
        from app.utils.auth import verify_token
        payload = verify_token(access_token)
        jti = payload.get("jti")
        
        # Revocar usando el store con Redis caído
        success = revocation_store.revoke_token(
            jti=jti,
            token_type="access",
            revoked_by=admin_user_data["email"],
            reason="Test revocation with Redis down",
            expires_at=payload.get("exp"),
            db=db_session
        )
        assert success
        
        # Verificar que token está revocado (usando SQL fallback)
        is_revoked = revocation_store.is_token_revoked(jti, db_session)
        assert is_revoked
        
        # Verificar que token revocado no funciona
        response = client.get("/users/1", headers=headers)
        assert response.status_code == 401

def test_no_unauthorized_access_with_redis_down(client, admin_user_data, db_session):
    """Test que no hay accesos indebidos con Redis caído"""
    # Crear usuario
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Login para obtener token
    login_data = {
        "username": admin_user_data["email"],
        "password": admin_user_data["contrasena"]
    }
    response = client.post("/token", data=login_data)
    access_token = response.json()["access_token"]
    
    # Simular Redis caído
    with patch('app.utils.revocation_store.redis.from_url') as mock_redis:
        mock_redis_client = MagicMock()
        mock_redis_client.ping.side_effect = Exception("Redis connection failed")
        mock_redis.return_value = mock_redis_client
        
        # Crear store con Redis caído
        revocation_store = RevocationStore()
        
        # Revocar token
        from app.utils.auth import verify_token
        payload = verify_token(access_token)
        jti = payload.get("jti")
        
        revocation_store.revoke_token(
            jti=jti,
            token_type="access",
            revoked_by=admin_user_data["email"],
            reason="Test no unauthorized access",
            expires_at=payload.get("exp"),
            db=db_session
        )
        
        # Verificar que no hay accesos indebidos (fail-closed)
        is_revoked = revocation_store.is_token_revoked(jti, db_session)
        assert is_revoked  # Debe estar revocado
        
        # Token revocado no debe funcionar
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/users/1", headers=headers)
        assert response.status_code == 401

def test_redis_status_metric_when_down():
    """Test que métrica de Redis muestra estado caído"""
    with patch('app.utils.revocation_store.redis.from_url') as mock_redis:
        mock_redis_client = MagicMock()
        mock_redis_client.ping.side_effect = Exception("Redis connection failed")
        mock_redis.return_value = mock_redis_client
        
        # Crear store con Redis caído
        revocation_store = RevocationStore()
        
        # Verificar estado
        status = revocation_store.get_redis_status()
        assert not status["available"]
        assert status["status"] == "disconnected"

def test_redis_connection_recovery():
    """Test que Redis se reconecta cuando vuelve a estar disponible"""
    with patch('app.utils.revocation_store.redis.from_url') as mock_redis:
        # Simular Redis caído inicialmente
        mock_redis_client = MagicMock()
        mock_redis_client.ping.side_effect = Exception("Redis connection failed")
        mock_redis.return_value = mock_redis_client
        
        revocation_store = RevocationStore()
        assert not revocation_store.redis_available
        
        # Simular Redis recuperado
        mock_redis_client.ping.return_value = True
        
        # Reconectar
        revocation_store._connect_redis()
        assert revocation_store.redis_available

def test_sql_fallback_consistency(client, admin_user_data, db_session):
    """Test que fallback SQL mantiene consistencia"""
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
    
    # Simular Redis caído
    with patch('app.utils.revocation_store.redis.from_url') as mock_redis:
        mock_redis_client = MagicMock()
        mock_redis_client.ping.side_effect = Exception("Redis connection failed")
        mock_redis.return_value = mock_redis_client
        
        revocation_store = RevocationStore()
        
        # Verificar que token funciona
        from app.utils.auth import verify_token
        payload = verify_token(access_token)
        jti = payload.get("jti")
        
        # Verificar que no está revocado inicialmente
        is_revoked_before = revocation_store.is_token_revoked(jti, db_session)
        assert not is_revoked_before
        
        # Revocar token
        revocation_store.revoke_token(
            jti=jti,
            token_type="access",
            revoked_by=admin_user_data["email"],
            reason="Test SQL consistency",
            expires_at=payload.get("exp"),
            db=db_session
        )
        
        # Verificar que está revocado
        is_revoked_after = revocation_store.is_token_revoked(jti, db_session)
        assert is_revoked_after
        
        # Verificar en base de datos directamente
        from app.models.db_models import TokenBlacklist
        blacklist_entry = db_session.query(TokenBlacklist).filter(
            TokenBlacklist.jti == jti
        ).first()
        assert blacklist_entry is not None
        assert blacklist_entry.jti == jti
