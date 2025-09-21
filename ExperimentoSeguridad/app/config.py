"""
Configuration module for the security microservice.
"""
import os
from typing import Dict, List

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# JWT configuration (RS256)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TTL_SEC = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # In seconds
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security configuration
CLOCK_SKEW_TOLERANCE_SECONDS = 60  # Clock skew tolerance ±60s
SKEW_SECONDS = 60  # Alias for compatibility

# RSA key configuration
KEYS_DIRECTORY = "keys"
KEYS_DIR = KEYS_DIRECTORY  # Alias for compatibility
DEFAULT_KID = "key-1"
ACTIVE_KID = os.getenv("ACTIVE_KID", DEFAULT_KID)

# JWT Claims configuration
JWT_ISS = os.getenv("JWT_ISS", "experimento-seguridad")
JWT_AUD = os.getenv("JWT_AUD", "api-users")

# Observability configuration
PROMETHEUS_ENABLED = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
METRICS_PATH = "/metrics"
PROMETHEUS_MULTIPROC_DIR = os.getenv("PROMETHEUS_MULTIPROC_DIR")

# RBAC configuration
RBAC_POLICIES: Dict[str, Dict[str, List[str]]] = {
    "admin": {
        "users": ["read", "create", "update", "delete"],
        "auth": ["rotate_keys", "view_blacklist"]
    },
    "user": {
        "users": ["read", "update"],
        "auth": []
    }
}
