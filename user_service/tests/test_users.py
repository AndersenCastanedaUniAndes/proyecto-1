import pytest
from datetime import timedelta
from sqlalchemy import inspect
from app.models import database as db
from sqlalchemy import create_engine
from unittest.mock import patch
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from jose import jwt

from app.models.db_models import Base, DBUser
from app.models.user import UserCreate, UserUpdate
from app.services.user_service import (
    get_db, hash_password, verify_password,
    create_access_token, create_user, login_user,
    get_user, update_user, delete_user
)
from config.config import SECRET_KEY, ALGORITHM


# --- CONFIGURACIÓN DEL ENTORNO DE PRUEBA ---
@pytest.fixture(scope="module")
def test_db():
    """Crea una BD SQLite temporal en memoria para pruebas"""
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


# --- TESTS DE FUNCIONALIDAD ---

def test_hash_and_verify_password():
    password = "test1234"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_create_user_success(test_db):
    user_data = UserCreate(
        nombre_usuario="Carlos",
        email="carlos@test.com",
        contrasena="pass123",
        rol="admin"
    )
    user = create_user(user_data, test_db)
    assert user.usuario_id is not None
    assert user.email == "carlos@test.com"
    assert verify_password("pass123", user.contrasena)


def test_create_user_duplicate_email(test_db):
    user_data = UserCreate(
        nombre_usuario="Carlos",
        email="carlos@test.com",
        contrasena="pass123",
        rol="user"
    )
    with pytest.raises(HTTPException) as exc:
        create_user(user_data, test_db)
    assert exc.value.status_code == 400
    assert "correo ya está registrado" in exc.value.detail


def test_login_user_success(test_db):
    result = login_user("carlos@test.com", "pass123", test_db)
    assert "access_token" in result
    decoded = jwt.decode(result["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "carlos@test.com"


def test_login_user_invalid_password(test_db):
    with pytest.raises(HTTPException) as exc:
        login_user("carlos@test.com", "wrongpass", test_db)
    assert exc.value.status_code == 401


def test_get_user_success(test_db):
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    user = get_user(admin.usuario_id, test_db, admin)
    assert user.email == "carlos@test.com"


def test_get_user_not_found(test_db):
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    with pytest.raises(HTTPException) as exc:
        get_user(999, test_db, admin)
    assert exc.value.status_code == 404


def test_update_user_success(test_db):
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    update_data = UserUpdate(nombre_usuario="Carlos Updated")
    updated_user = update_user(admin.usuario_id, update_data, test_db, admin)
    assert updated_user.nombre_usuario == "Carlos Updated"


def test_delete_user_no_permissions(test_db):
    # Crear un usuario "normal"
    normal_user = UserCreate(
        nombre_usuario="Pedro",
        email="pedro@test.com",
        contrasena="pass123",
        rol="user"
    )
    created_user = create_user(normal_user, test_db)

    # Intentar borrar con permisos de usuario normal
    with pytest.raises(HTTPException) as exc:
        delete_user(created_user.usuario_id, test_db, created_user)
    assert exc.value.status_code == 403


def test_delete_user_success(test_db):
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    pedro = test_db.query(DBUser).filter(DBUser.email == "pedro@test.com").first()
    result = delete_user(pedro.usuario_id, test_db, admin)
    assert result["message"] == "Usuario eliminado con éxito."

def test_create_user_missing_fields(test_db):
    user_data = UserCreate(
        nombre_usuario="",   # En lugar de None
        email="incompleto@test.com",
        contrasena="1234",
        rol=""               # En lugar de None
    )
    with pytest.raises(HTTPException) as exc:
        create_user(user_data, test_db)
    assert exc.value.status_code == 422
    assert "Faltan campos obligatorios" in exc.value.detail


def test_update_user_not_found(test_db):
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    update_data = UserUpdate(nombre_usuario="Nuevo Nombre")
    with pytest.raises(HTTPException) as exc:
        update_user(9999, update_data, test_db, admin)
    assert exc.value.status_code == 404

def test_update_user_no_fields(test_db):
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    update_data = UserUpdate()
    with pytest.raises(HTTPException) as exc:
        update_user(admin.usuario_id, update_data, test_db, admin)
    assert exc.value.status_code == 422

def test_delete_user_not_found(test_db):
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    with pytest.raises(HTTPException) as exc:
        delete_user(9999, test_db, admin)
    assert exc.value.status_code == 404

import pytest
from datetime import timedelta

def test_create_access_token_invalid_secret(monkeypatch):
    from app.services import user_service
    monkeypatch.setattr(user_service, "SECRET_KEY", None)
    with pytest.raises(HTTPException):
        user_service.create_access_token({"sub": "test@test.com"}, timedelta(minutes=1))

from app.services import user_service




def test_get_db_returns_session(capfd):
    gen = get_db()
    db = next(gen)
    assert hasattr(db, "query")
    try:
        next(gen)
    except StopIteration:
        pass
    captured = capfd.readouterr()
    assert "Tablas" in captured.out or captured.out == ""

def test_create_access_token_valid_token():
    """Verifica creación de token JWT válido"""
    data = {"sub": "user@test.com"}
    token = create_access_token(data, timedelta(minutes=1))
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "user@test.com"
    assert "exp" in decoded


def test_verify_password_invalid():
    """Verifica que contraseñas no coincidentes retornen False"""
    password = "abc123"
    hashed = hash_password(password)
    assert not verify_password("xyz789", hashed)


def test_delete_user_as_admin_fails_on_nonexistent(test_db):
    """Prueba que borrar un usuario inexistente lanza 404"""
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    with pytest.raises(HTTPException) as exc:
        delete_user(99999, test_db, admin)
    assert exc.value.status_code == 404


def test_login_user_not_found(test_db):
    """Verifica intento de login con correo inexistente"""
    with pytest.raises(HTTPException) as exc:
        login_user("noexiste@test.com", "pass123", test_db)
    assert exc.value.status_code == 401
    assert "Correo o contraseña incorrectos" in exc.value.detail



def test_update_user_as_non_admin(test_db):
    """Verifica que un usuario normal no pueda modificar otro"""
    user = UserCreate(
        nombre_usuario="Mario",
        email="mario@test.com",
        contrasena="pass123",
        rol="user"
    )
    created_user = create_user(user, test_db)

    # El mismo usuario intenta modificar a otro
    with pytest.raises(HTTPException) as exc:
        update_user(1, UserUpdate(nombre_usuario="Hack"), test_db, created_user)
    assert exc.value.status_code == 403
