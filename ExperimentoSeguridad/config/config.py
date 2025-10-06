# Configuración de la base de datos, claves secretas, etc.
#DATABASE_URL = "sqlite:///./users.db"
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/users"  # Para PostgreSQL

# Configuración de JWT
ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Configuración de claves RSA
PRIVATE_KEY_PATH = "keys/private_key.pem"
PUBLIC_KEY_PATH = "keys/public_key.pem"
JWKS_PATH = "keys/jwks.json"
KEY_ID = "default"

# Configuración de Redis
REDIS_URL = "redis://localhost:6379/0"
REDIS_BLACKLIST_PREFIX = "blacklist:"

# Configuración de seguridad
CLOCK_SKEW_TOLERANCE_SECONDS = 60  # Tolerancia para clock skew ±60s

# Configuración de métricas
PROMETHEUS_PORT = 8001
