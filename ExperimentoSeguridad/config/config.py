# Configuración de la base de datos, claves secretas, etc.
DATABASE_URL = "sqlite:///./users.db"

# Configuración de JWT (ahora usa RS256)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Configuración de seguridad
CLOCK_SKEW_TOLERANCE_SECONDS = 60  # Tolerancia para clock skew ±60s

# Configuración de claves RSA
KEYS_DIRECTORY = "keys"
DEFAULT_KID = "key-1"
