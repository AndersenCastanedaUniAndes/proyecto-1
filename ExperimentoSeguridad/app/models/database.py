from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de conexión a la base de datos (ajústala según tu motor)
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
# Para PostgreSQL sería algo como:
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

# Crea el motor de conexión
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Solo para SQLite
)

# Configuración de sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependencia para obtener la sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
