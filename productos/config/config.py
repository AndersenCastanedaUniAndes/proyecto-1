# Configuración de la base de datos, claves secretas, etc.
#DATABASE_URL = "sqlite:///./products.db"
DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5432/products"
SECRET_KEY = "user-secret-key"
# Configuración de JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30