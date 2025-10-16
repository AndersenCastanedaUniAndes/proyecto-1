import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import status

from app.models.db_models import Base, DBUser
from app.models.user import UserCreate, UserUpdate
from app.main import app  # Asegúrate de importar tu instancia principal de FastAPI
from app.services import user_service
from app.routes import user_routes


# 🔹 Base temporal en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_user_routes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🔹 Crear tablas
Base.metadata.create_all(bind=engine)

# 🔹 Fixture DB
@pytest.fixture(scope="function")
def db():
    session = TestingSessionLocal()
    yield session
    session.close()

# 🔹 Sobrescribir dependencia de FastAPI
@pytest.fixture(scope="function", autouse=True)
def override_get_db(monkeypatch, db):
    def _get_db_override():
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[user_service.get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()

# 🔹 Cliente de pruebas
@pytest.fixture(scope="module")
def client():
    return TestClient(app)

# Dependencia simulada de BD para FastAPI
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Sobrescribir dependencias de BD
app.dependency_overrides[user_service.get_db] = override_get_db
app.dependency_overrides[user_routes.get_db] = override_get_db

client = TestClient(app)


# --- FIXTURES ---
@pytest.fixture(scope="module")
def db():
    db = TestingSessionLocal()
    yield db
    db.close()


# --- TESTS ---








def test_authenticate_user_invalid_credentials(db):
    form_data = {"username": "juan@test.com", "password": "wrong"}
    response = client.post("/token", data=form_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Correo o contraseña incorrectos" in response.json()["detail"]


def test_authenticate_user_not_found(db):
    form_data = {"username": "noexiste@test.com", "password": "secret"}
    response = client.post("/token", data=form_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_read_user_success(db):
    # Crear admin manualmente
    admin = db.query(DBUser).filter(DBUser.email == "juan@test.com").first()
    token = user_service.create_access_token({"sub": admin.email})

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/users/{admin.usuario_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == admin.email


def test_update_user_success(db):
    admin = db.query(DBUser).filter(DBUser.email == "juan@test.com").first()
    token = user_service.create_access_token({"sub": admin.email})

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"nombre_usuario": "Juan Actualizado"}
    response = client.put(f"/users/{admin.usuario_id}", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["nombre_usuario"] == "Juan Actualizado"


def test_delete_user_success(db):
    # Crear un usuario normal
    user = DBUser(
        nombre_usuario="Pedro",
        email="pedro@test.com",
        contrasena=user_service.hash_password("secret"),
        rol="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Borrar como admin
    admin = db.query(DBUser).filter(DBUser.email == "juan@test.com").first()
    token = user_service.create_access_token({"sub": admin.email})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete(f"/users/{user.usuario_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Usuario eliminado con éxito."


def test_authenticate_user_internal_error(monkeypatch, db):
    """Simula un error inesperado en authenticate_user"""
    def mock_query_error(*args, **kwargs):
        raise Exception("DB crash")

    monkeypatch.setattr(db, "query", mock_query_error)
    with pytest.raises(Exception):
        user_routes.authenticate_user(db, "email@test.com", "1234")
