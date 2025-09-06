"""
Servicio para manejo de Redis con fallback a SQL
Implementa blacklist de tokens con alta disponibilidad
"""

import redis
import json
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from config.config import REDIS_URL, REDIS_BLACKLIST_PREFIX
from app.models.db_models import TokenBlacklist
import logging

logger = logging.getLogger(__name__)

class RedisService:
    """Servicio para manejo de Redis con fallback a SQL"""
    
    def __init__(self):
        self.redis_client = None
        self.redis_available = False
        self.connect_redis()
    
    def connect_redis(self):
        """Intenta conectar a Redis"""
        try:
            self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            # Test de conexión
            self.redis_client.ping()
            self.redis_available = True
            logger.info("✅ Redis conectado exitosamente")
        except Exception as e:
            logger.warning(f"⚠️ Redis no disponible: {e}")
            self.redis_available = False
    
    def is_redis_available(self) -> bool:
        """Verifica si Redis está disponible"""
        if not self.redis_available:
            return False
        
        try:
            self.redis_client.ping()
            return True
        except Exception:
            self.redis_available = False
            return False
    
    def add_to_blacklist(self, jti: str, token_type: str, expires_at: datetime, 
                        revoked_by: str, reason: str, db: Session) -> bool:
        """Agrega un token a la blacklist (Redis + SQL fallback)"""
        try:
            # Intentar agregar a Redis primero
            if self.is_redis_available():
                blacklist_data = {
                    "jti": jti,
                    "token_type": token_type,
                    "expires_at": expires_at.isoformat(),
                    "revoked_at": datetime.utcnow().isoformat(),
                    "revoked_by": revoked_by,
                    "reason": reason
                }
                
                # Calcular TTL en segundos
                ttl = int((expires_at - datetime.utcnow()).total_seconds())
                if ttl > 0:
                    key = f"{REDIS_BLACKLIST_PREFIX}{jti}"
                    self.redis_client.setex(
                        key, 
                        ttl, 
                        json.dumps(blacklist_data)
                    )
                    logger.info(f"✅ Token {jti} agregado a Redis blacklist")
            
            # Siempre agregar a SQL como fallback
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
            logger.info(f"✅ Token {jti} agregado a SQL blacklist")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al agregar token a blacklist: {e}")
            db.rollback()
            return False
    
    def is_token_blacklisted(self, jti: str, db: Session) -> bool:
        """Verifica si un token está en la blacklist (Redis + SQL fallback)"""
        try:
            # Intentar consultar Redis primero
            if self.is_redis_available():
                key = f"{REDIS_BLACKLIST_PREFIX}{jti}"
                result = self.redis_client.get(key)
                if result:
                    logger.debug(f"✅ Token {jti} encontrado en Redis blacklist")
                    return True
            
            # Fallback a SQL
            blacklist_entry = db.query(TokenBlacklist).filter(
                TokenBlacklist.jti == jti
            ).first()
            
            if blacklist_entry:
                logger.debug(f"✅ Token {jti} encontrado en SQL blacklist")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error al verificar blacklist: {e}")
            # En caso de error, asumir que no está en blacklist
            return False
    
    def get_blacklist_entries(self, limit: int = 100, db: Session = None) -> List[dict]:
        """Obtiene entradas de la blacklist (Redis + SQL)"""
        entries = []
        
        try:
            # Intentar obtener de Redis primero
            if self.is_redis_available():
                pattern = f"{REDIS_BLACKLIST_PREFIX}*"
                keys = self.redis_client.keys(pattern)
                
                for key in keys[:limit]:
                    data = self.redis_client.get(key)
                    if data:
                        entry = json.loads(data)
                        entries.append(entry)
                
                if entries:
                    logger.info(f"✅ {len(entries)} entradas obtenidas de Redis")
                    return entries
            
            # Fallback a SQL
            if db:
                db_entries = db.query(TokenBlacklist).order_by(
                    TokenBlacklist.revoked_at.desc()
                ).limit(limit).all()
                
                for entry in db_entries:
                    entries.append({
                        "jti": entry.jti,
                        "token_type": entry.token_type,
                        "expires_at": entry.expires_at.isoformat(),
                        "revoked_at": entry.revoked_at.isoformat(),
                        "revoked_by": entry.revoked_by,
                        "reason": entry.reason
                    })
                
                logger.info(f"✅ {len(entries)} entradas obtenidas de SQL")
            
            return entries
            
        except Exception as e:
            logger.error(f"❌ Error al obtener blacklist: {e}")
            return []
    
    def get_redis_status(self) -> dict:
        """Obtiene el estado de Redis"""
        return {
            "available": self.is_redis_available(),
            "url": REDIS_URL,
            "prefix": REDIS_BLACKLIST_PREFIX
        }
    
    def clear_blacklist(self, db: Session) -> bool:
        """Limpia la blacklist (Redis + SQL)"""
        try:
            # Limpiar Redis
            if self.is_redis_available():
                pattern = f"{REDIS_BLACKLIST_PREFIX}*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"✅ {len(keys)} entradas eliminadas de Redis")
            
            # Limpiar SQL
            db.query(TokenBlacklist).delete()
            db.commit()
            logger.info("✅ Blacklist SQL limpiada")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al limpiar blacklist: {e}")
            db.rollback()
            return False

# Instancia global del servicio Redis
redis_service = RedisService()
