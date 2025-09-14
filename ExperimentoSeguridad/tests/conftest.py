"""
Configuración de tests para el experimento de seguridad
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.db_models import Base
from config.config import DATABASE_URL

# Base de datos de prueba
TEST_DATABASE_URL = "sqlite:///./test_users.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Crear event loop para tests asíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Crear sesión de base de datos para cada test"""
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión
    session = TestingSessionLocal()
    
    yield session
    
    # Limpiar después del test
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Cliente de prueba FastAPI"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    from app.services.user_service import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user_data():
    """Datos de usuario administrador para tests"""
    return {
        "nombre_usuario": "admin_test",
        "email": "admin@test.com",
        "contrasena": "admin123",
        "rol": "admin"
    }

@pytest.fixture
def regular_user_data():
    """Datos de usuario regular para tests"""
    return {
        "nombre_usuario": "user_test",
        "email": "user@test.com",
        "contrasena": "user123",
        "rol": "user"
    }

@pytest.fixture
def admin_token(client, admin_user_data):
    """Token de administrador para tests"""
    # Crear usuario admin
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    # Login
    login_data = {
        "username": admin_user_data["email"],
        "password": admin_user_data["contrasena"]
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    
    return response.json()["access_token"]

@pytest.fixture
def user_token(client, regular_user_data):
    """Token de usuario regular para tests"""
    # Crear usuario regular
    response = client.post("/users/", json=regular_user_data)
    assert response.status_code == 200
    
    # Login
    login_data = {
        "username": regular_user_data["email"],
        "password": regular_user_data["contrasena"]
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    
    return response.json()["access_token"]
