import os
from dotenv import load_dotenv
load_dotenv()

# Configuración de la base de datos, claves secretas, etc.
#DATABASE_URL = "sqlite:///./products.db"
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

# Configuración de JWT
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
