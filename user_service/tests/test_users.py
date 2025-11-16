import pytest
from jose import JWTError
from datetime import timedelta
from sqlalchemy import inspect
from app.models import database as db
from sqlalchemy import create_engine
from unittest.mock import patch
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from jose import jwt

from app.models.db_models import Base, DBUser, PlanVenta, PlanVendedor
from app.models.user import UserCreate, UserUpdate
from app.services.user_service import (
    get_db, hash_password, verify_password,
    create_access_token, create_user, login_user,
    get_user, update_user, delete_user,create_vendedor,
    read_vendedores,
    read_vendedor,
    update_vendedor,
    delete_vendedor, init_db,get_current_user,  crear_plan_venta,
    listar_planes_venta,
    actualizar_plan_de_venta,
    eliminar_plan_de_venta,
    obtener_plan_venta_por_id
)
from config.config import SECRET_KEY, ALGORITHM



# ----------------------------
# init_db()
# ----------------------------
def test_init_db_exception(monkeypatch):
    def bad_create_all(bind): raise Exception("DB error")
    from app.services import user_service
    monkeypatch.setattr(user_service.Base.metadata, "create_all", bad_create_all)
    with pytest.raises(Exception):
        init_db()

# ----------------------------
# create_vendedor y create_user
# ----------------------------
def test_create_vendedor_campos_incompletos(test_db):
    from app.models.user import UserCreate
    user = UserCreate(nombre_usuario="", email="", contrasena="", rol="")
    with pytest.raises(HTTPException) as e:
        create_vendedor(user, test_db, None)
    assert e.value.status_code == 422






# ----------------------------
# update_vendedor y update_user
# ----------------------------
def test_update_vendedor_usuario_no_encontrado(test_db):
    from app.models.user import UserUpdate
    user = UserUpdate(nombre_usuario="Nuevo")
    with pytest.raises(HTTPException) as e:
        update_vendedor(999, user, test_db, None)
    assert e.value.status_code == 404






def test_delete_vendedor_no_existe(test_db):
    with pytest.raises(HTTPException) as e:
        delete_vendedor(999, test_db, None)
    assert e.value.status_code == 404


# ----------------------------
# get_current_user
# ----------------------------
def test_get_current_user_token_invalido(monkeypatch, test_db):
    from app.services import user_service
    monkeypatch.setattr(user_service.jwt, "decode", lambda *a, **k: (_ for _ in ()).throw(JWTError()))
    with pytest.raises(HTTPException) as e:
        user_service.get_current_user(token="badtoken", db=test_db)
    assert e.value.status_code == 401


def test_get_current_user_sin_sub(monkeypatch, test_db):
    from app.services import user_service
    monkeypatch.setattr(user_service.jwt, "decode", lambda *a, **k: {})
    with pytest.raises(HTTPException) as e:
        user_service.get_current_user(token="x", db=test_db)
    assert e.value.status_code == 401


# ----------------------------
# create_access_token
# ----------------------------
def test_create_access_token_error(monkeypatch):
    from app.services import user_service
    monkeypatch.setattr(user_service.jwt, "encode", lambda *a, **k: (_ for _ in ()).throw(Exception("JWT fail")))
    from datetime import timedelta
    with pytest.raises(HTTPException) as e:
        user_service.create_access_token({"sub": "abc"}, timedelta(minutes=5))
    assert e.value.status_code == 500

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




def test_create_vendedor_success(test_db):
    """Crea correctamente un vendedor"""
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    vendedor_data = UserCreate(
        nombre_usuario="Vendedor1",
        email="vendedor1@test.com",
        contrasena="vpass123",
        rol="vendedor"
    )
    vendedor = create_vendedor(vendedor_data, test_db, admin)
    assert vendedor.usuario_id is not None
    assert vendedor.rol == "vendedor"
    assert vendedor.email == "vendedor1@test.com"


def test_create_vendedor_duplicate_email(test_db):
    """Evita crear un vendedor con correo ya registrado"""
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    vendedor_data = UserCreate(
        nombre_usuario="Duplicado",
        email="vendedor1@test.com",
        contrasena="otra",
        rol="vendedor"
    )
    with pytest.raises(HTTPException) as exc:
        create_vendedor(vendedor_data, test_db, admin)
    assert exc.value.status_code == 400
    assert "correo ya está registrado" in exc.value.detail


def test_create_vendedor_missing_fields(test_db):
    """Evita crear vendedor con campos vacíos"""
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    vendedor_data = UserCreate(
        nombre_usuario="",
        email="",
        contrasena="",
        rol=""
    )
    with pytest.raises(HTTPException) as exc:
        create_vendedor(vendedor_data, test_db, admin)
    assert exc.value.status_code == 422
    assert "Faltan campos obligatorios" in exc.value.detail


def test_read_vendedores_success(test_db):
    """Obtiene correctamente la lista de vendedores"""
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    vendedores = read_vendedores(test_db, skip=0, limit=10, current_user=admin)
    assert isinstance(vendedores, list)
    assert any(v.rol == "vendedor" for v in vendedores)


def test_read_vendedor_success(test_db):
    """Obtiene correctamente un vendedor existente"""
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    vendedor = test_db.query(DBUser).filter(DBUser.email == "vendedor1@test.com").first()
    result = read_vendedor(vendedor.usuario_id, test_db, admin)
    assert result.email == "vendedor1@test.com"


def test_read_vendedor_not_found(test_db):
    """Lanza 404 al consultar un vendedor inexistente"""
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    with pytest.raises(HTTPException) as exc:
        read_vendedor(99999, test_db, admin)
    assert exc.value.status_code == 404


def test_update_vendedor_success(test_db):
    """Actualiza correctamente los datos de un vendedor"""
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    vendedor = test_db.query(DBUser).filter(DBUser.email == "vendedor1@test.com").first()
    update_data = UserUpdate(nombre_usuario="Vendedor Actualizado")
    updated = update_vendedor(vendedor.usuario_id, update_data, test_db, admin)
    assert updated.nombre_usuario == "Vendedor Actualizado"


def test_update_vendedor_not_found(test_db):
    """Lanza 404 al intentar actualizar un vendedor inexistente"""
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    update_data = UserUpdate(nombre_usuario="No existe")
    with pytest.raises(HTTPException) as exc:
        update_vendedor(9999, update_data, test_db, admin)
    assert exc.value.status_code == 404


def test_delete_vendedor_success(test_db):
    """Elimina correctamente un vendedor existente"""
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    vendedor = test_db.query(DBUser).filter(DBUser.email == "vendedor1@test.com").first()
    result = delete_vendedor(vendedor.usuario_id, test_db, admin)
    assert result["message"] == "Usuario eliminado con éxito."


def test_delete_vendedor_not_found(test_db):
    """Lanza 404 si intenta eliminar un vendedor inexistente"""
    admin = test_db.query(DBUser).filter(DBUser.email == "carlos@test.com").first()
    with pytest.raises(HTTPException) as exc:
        delete_vendedor(99999, test_db, admin)
    assert exc.value.status_code == 404

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


# ============================================================
# 🔧 FIXTURES AUXILIARES
# ============================================================

@pytest.fixture
def vendedor_test(test_db):
    test_db.query(DBUser).filter(DBUser.email == "pedro@test.com").delete()
    test_db.commit()

    vendedor = DBUser(
        nombre_usuario="Pedro Perez",
        email="pedro@test.com",
        contrasena="hash",
        rol="vendedor",
        estado=True
    )
    test_db.add(vendedor)
    test_db.commit()
    test_db.refresh(vendedor)
    return vendedor

@pytest.fixture
def plan_existente(test_db, vendedor_test):
    """Crea un plan base para pruebas"""
    plan = PlanVenta(periodo="mensual", valor_ventas=10000, estado="activo")
    test_db.add(plan)
    test_db.flush()
    asignacion = PlanVendedor(plan_id=plan.id, vendedor_id=vendedor_test.usuario_id)
    test_db.add(asignacion)
    test_db.commit()
    test_db.refresh(plan)
    return plan


# ============================================================
# 🧪 CREAR PLAN DE VENTA
# ============================================================

def test_crear_plan_venta_success(test_db, vendedor_test):
    result = crear_plan_venta("trimestral", 50000, [vendedor_test.usuario_id], test_db)
    assert "plan_id" in result
    plan = test_db.query(PlanVenta).get(result["plan_id"])
    assert plan.periodo == "trimestral"
    assert float(plan.valor_ventas) == 50000


 

def test_crear_plan_venta_sin_vendedores(test_db):
    with pytest.raises(HTTPException) as exc:
        crear_plan_venta("mensual", 1000, [], test_db)
    assert exc.value.status_code == 500
    assert "Debe asignar al menos un vendedor" in exc.value.detail


def test_crear_plan_venta_valor_negativo(test_db, vendedor_test):
    with pytest.raises(HTTPException) as exc:
        crear_plan_venta("anual", -50, [vendedor_test.usuario_id], test_db)
    assert exc.value.status_code == 500
    assert "no puede ser negativo" in exc.value.detail


# ============================================================
# 📋 LISTAR PLANES DE VENTA
# ============================================================

def test_listar_planes_venta(test_db, plan_existente):
    result = listar_planes_venta(test_db, None)
    assert isinstance(result, list)
    assert any(plan["periodo"] == "mensual" for plan in result)
    assert "vendedores" in result[0]


# ============================================================
# 🔍 OBTENER PLAN POR ID
# ============================================================

def test_obtener_plan_venta_por_id_success(test_db, plan_existente):
    result = obtener_plan_venta_por_id(plan_existente.id, test_db, None)
    assert result["id"] == plan_existente.id
    assert result["periodo"] == "mensual"
    assert len(result["vendedores"]) == 1


def test_obtener_plan_venta_por_id_not_found(test_db):
    with pytest.raises(HTTPException) as exc:
        obtener_plan_venta_por_id(99999, test_db, None)
    assert exc.value.status_code == 404


# ============================================================
# ✏️ ACTUALIZAR PLAN DE VENTA
# ============================================================

def test_actualizar_plan_de_venta_success(test_db, plan_existente, vendedor_test):
    result = actualizar_plan_de_venta(
        plan_existente.id,
        "anual",
        80000.0,
        "completado",
        [vendedor_test.usuario_id],
        test_db,
        None
    )
    assert "Plan actualizado" in result["message"]

    actualizado = test_db.query(PlanVenta).get(plan_existente.id)
    assert actualizado.periodo == "anual"
    assert actualizado.estado == "completado"
    assert float(actualizado.valor_ventas) == 80000.0


def test_actualizar_plan_de_venta_inexistente(test_db):
    with pytest.raises(HTTPException) as exc:
        actualizar_plan_de_venta(9999, "mensual", 1000, "activo", [], test_db, None)
    assert exc.value.status_code == 404


def test_actualizar_plan_de_venta_estado_invalido(test_db, plan_existente):
    with pytest.raises(HTTPException) as exc:
        actualizar_plan_de_venta(plan_existente.id, None, None, "cerrado", None, test_db, None)
    assert exc.value.status_code == 500
    assert "Estado inválido" in exc.value.detail


def test_actualizar_plan_de_venta_valor_negativo(test_db, plan_existente):
    with pytest.raises(HTTPException) as exc:
        actualizar_plan_de_venta(plan_existente.id, None, -10, None, None, test_db, None)
    assert exc.value.status_code == 500
    assert "no puede ser negativo" in exc.value.detail


# ============================================================
# 🗑️ ELIMINAR PLAN DE VENTA
# ============================================================

def test_eliminar_plan_de_venta_success(test_db, plan_existente):
    result = eliminar_plan_de_venta(plan_existente.id, test_db, None)
    assert "eliminado" in result["message"]


def test_eliminar_plan_de_venta_not_found(test_db):
    with pytest.raises(HTTPException) as exc:
        eliminar_plan_de_venta(88888, test_db, None)
    assert exc.value.status_code == 404