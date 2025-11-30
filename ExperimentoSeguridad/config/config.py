import os
from typing import Optional

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Configuración de JWT (ahora usa RS256)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TTL_SEC = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # En segundos
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Configuración de seguridad
CLOCK_SKEW_TOLERANCE_SECONDS = 60  # Tolerancia para clock skew ±60s
SKEW_SECONDS = 61  # Alias para compatibilidad

# Configuración de claves RSA
KEYS_DIRECTORY = "keys"
KEYS_DIR = KEYS_DIRECTORY  # Alias para compatibilidad
DEFAULT_KID = "key-1"
ACTIVE_KID = os.getenv("ACTIVE_KID", DEFAULT_KID)

# Configuración JWT Claims
JWT_ISS = os.getenv("JWT_ISS", "experimento-seguridad")
JWT_AUD = os.getenv("JWT_AUD", "api-users")

# Configuración de observabilidad
PROMETHEUS_ENABLED = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
METRICS_PATH = "/metrics"

# Configuración de RBAC
RBAC_POLICIES = {
    "admin": {
        "users": ["read", "create", "update", "delete"],
        "auth": ["rotate_keys", "view_blacklist"]
    },
    "user": {
        "users": ["read", "update"],
        "auth": []
    }
}
