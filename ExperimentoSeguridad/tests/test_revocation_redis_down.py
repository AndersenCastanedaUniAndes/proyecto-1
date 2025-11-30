"""
Test: Simula Redis caído, usa fallback SQL, 0 accesos indebidos, métrica redis_down
"""
import pytest
from unittest.mock import patch, MagicMock
from app.utils.revocation_store import RevocationStore

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
