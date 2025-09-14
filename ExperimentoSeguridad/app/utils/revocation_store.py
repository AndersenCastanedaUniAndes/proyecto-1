"""
Sistema de revocación de tokens con Redis + fallback SQL (fail-closed)
"""
import redis
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from config.config import REDIS_URL
from app.models.db_models import TokenBlacklist

logger = logging.getLogger(__name__)

class RevocationStore:
    """Store para revocación de tokens con Redis + fallback SQL"""
    
    def __init__(self, redis_url: str = REDIS_URL):
        self.redis_url = redis_url
        self.redis_client = None
        self.redis_available = False
        self._connect_redis()
    
    def _connect_redis(self):
        """Intenta conectar a Redis"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test de conexión
            self.redis_client.ping()
            self.redis_available = True
            logger.info("✅ Redis conectado exitosamente")
        except Exception as e:
            logger.warning(f"⚠️ Redis no disponible: {e}. Usando fallback SQL")
            self.redis_available = False
            self.redis_client = None
    
    def is_token_revoked(self, jti: str, db: Session) -> bool:
        """
        Verifica si un token está revocado (fail-closed)
        Intenta Redis primero, fallback a SQL
        """
        try:
            # Intentar Redis primero
            if self.redis_available and self.redis_client:
                try:
                    result = self.redis_client.get(f"revoked:{jti}")
                    if result is not None:
                        return True  # Token encontrado en Redis = revocado
                except Exception as e:
                    logger.warning(f"Error consultando Redis: {e}")
                    self.redis_available = False
            
            # Fallback a SQL
            return self._is_token_revoked_sql(jti, db)
            
        except Exception as e:
            logger.error(f"Error verificando revocación: {e}")
            # Fail-closed: si hay error, asumir que está revocado
            return True
    
    def _is_token_revoked_sql(self, jti: str, db: Session) -> bool:
        """Verifica revocación en SQL"""
        try:
            blacklist_entry = db.query(TokenBlacklist).filter(
                TokenBlacklist.jti == jti
            ).first()
            return blacklist_entry is not None
        except Exception as e:
            logger.error(f"Error consultando SQL: {e}")
            return True  # Fail-closed
    
    def revoke_token(self, jti: str, token_type: str, revoked_by: str, 
                    reason: str, expires_at: datetime, db: Session) -> bool:
        """
        Revoca un token (almacena en Redis + SQL)
        """
        try:
            # Datos del token revocado
            token_data = {
                "jti": jti,
                "token_type": token_type,
                "revoked_by": revoked_by,
                "reason": reason,
                "revoked_at": datetime.utcnow().isoformat(),
                "expires_at": expires_at.isoformat()
            }
            
            # Almacenar en Redis (si está disponible)
            if self.redis_available and self.redis_client:
                try:
                    # Calcular TTL para Redis (hasta expiración del token)
                    ttl_seconds = int((expires_at - datetime.utcnow()).total_seconds())
                    if ttl_seconds > 0:
                        self.redis_client.setex(
                            f"revoked:{jti}",
                            ttl_seconds,
                            json.dumps(token_data)
                        )
                        logger.info(f"Token {jti} revocado en Redis")
                except Exception as e:
                    logger.warning(f"Error almacenando en Redis: {e}")
                    self.redis_available = False
            
            # Almacenar en SQL (siempre)
            self._revoke_token_sql(jti, token_type, revoked_by, reason, expires_at, db)
            
            return True
            
        except Exception as e:
            logger.error(f"Error revocando token: {e}")
            return False
    
    def _revoke_token_sql(self, jti: str, token_type: str, revoked_by: str, 
                         reason: str, expires_at: datetime, db: Session):
        """Almacena token revocado en SQL"""
        try:
            # Verificar si ya existe
            existing = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
            if existing:
                return  # Ya está revocado
            
            # Crear nueva entrada
            blacklist_entry = TokenBlacklist(
                jti=jti,
                token_type=token_type,
                expires_at=expires_at,
                revoked_at=datetime.utcnow(),
                revoked_by=revoked_by,
                reason=reason
            )
            
            db.add(blacklist_entry)
            db.commit()
            logger.info(f"Token {jti} revocado en SQL")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error almacenando en SQL: {e}")
            raise
    
    def get_redis_status(self) -> Dict[str, Any]:
        """Obtiene el estado de Redis"""
        return {
            "available": self.redis_available,
            "url": self.redis_url,
            "status": "connected" if self.redis_available else "disconnected"
        }
    
    def cleanup_expired_tokens(self, db: Session) -> int:
        """Limpia tokens expirados de la blacklist SQL"""
        try:
            now = datetime.utcnow()
            expired_count = db.query(TokenBlacklist).filter(
                TokenBlacklist.expires_at < now
            ).count()
            
            if expired_count > 0:
                db.query(TokenBlacklist).filter(
                    TokenBlacklist.expires_at < now
                ).delete()
                db.commit()
                logger.info(f"Limpiados {expired_count} tokens expirados")
            
            return expired_count
            
        except Exception as e:
            logger.error(f"Error limpiando tokens expirados: {e}")
            return 0

# Instancia global
revocation_store = RevocationStore()
