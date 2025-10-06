from app.services.user_service import generate_jti, hash_password, hash_token, verify_password
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi import HTTPException
from pydantic import ValidationError
from datetime import datetime, timedelta


from app.models.db_models import DBUser, RefreshToken, TokenBlacklist
from app.models.user import UserCreate, UserUpdate

  
from app.services.user_service import (
    hash_password, verify_password, create_access_token, create_user, login_user,
    get_user, update_user, delete_user, create_refresh_token, verify_refresh_token,
    revoke_token, is_token_blacklisted, get_blacklist_entries, generate_jti, hash_token
)

@pytest.fixture
def db():
    db = MagicMock(spec=Session)
    db.query().filter().first.return_value = None
    db.query().filter().all.return_value = []
    db.query().filter().first.side_effect = lambda: None
    return db

@pytest.fixture
def user():
    return UserCreate(
        nombre_usuario="testuser",
        email="test@example.com",
        contrasena="password123",
        rol="user"
    )

@pytest.fixture
def db_user():
    return DBUser(
        usuario_id=1,
        nombre_usuario="testuser",
        email="test@example.com",
        contrasena=hash_password("password123"),
        rol="user"
    )

def test_hash_and_verify_password():
    pw = "secret"
    hashed = hash_password(pw)
    assert verify_password(pw, hashed)
    assert not verify_password("wrong", hashed)

@patch("app.services.user_service.key_service")
def test_create_access_token(mock_key_service):
    mock_key_service.get_current_kid.return_value = "kid1"
    mock_key_service.get_private_key.return_value = "secret"
    data = {"sub": "test@example.com", "type": "access"}
    with patch("app.services.user_service.jwt.encode", return_value="token"):
        token = create_access_token(data)
        assert token == "token"

@patch("app.services.user_service.key_service")
def test_create_access_token_error(mock_key_service):
    mock_key_service.get_current_kid.side_effect = Exception("fail")
    data = {"sub": "test@example.com", "type": "access"}
    with pytest.raises(HTTPException):
        create_access_token(data)

def test_generate_jti_and_hash_token():
    jti = generate_jti()
    assert isinstance(jti, str)
    token_hash = hash_token("token")
    assert isinstance(token_hash, str)

def test_create_user_success(db, user):
    db.query().filter().first.return_value = None
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    result = create_user(user, db)
    assert result is not None

def test_create_user_missing_fields(db):
    user = UserCreate(nombre_usuario="", email="", contrasena="", rol="")
    with pytest.raises(HTTPException):
        create_user(user, db)

def test_login_user_wrong_password(db, db_user):
    db.query().filter().first.return_value = db_user
    with patch("app.services.user_service.verify_password", return_value=False):
        with pytest.raises(HTTPException):
            login_user(db_user.email, "wrong", db)

def test_login_user_no_user(db):
    db.query().filter().first.return_value = None
    with pytest.raises(HTTPException):
        login_user("nouser@example.com", "password", db)


def test_get_user_not_found(db, db_user):
    db.query().filter().first.return_value = None
    with pytest.raises(HTTPException):
        get_user(999, db, db_user)


def test_update_user_no_fields(db, db_user):
    user_update = UserUpdate()
    with pytest.raises(HTTPException):
        update_user(db_user.usuario_id, user_update, db, db_user)

def test_update_user_not_found(db):
    db.query().filter().first.return_value = None
    user_update = UserUpdate(nombre_usuario="newname")
    with pytest.raises(HTTPException):
        update_user(999, user_update, db, DBUser())

def test_delete_user_success(db, db_user):
    db.query().filter().first.side_effect = [db_user, db_user]
    db.query().filter().all.return_value = []
    db.commit = MagicMock()
    db.delete = MagicMock()
    admin_user = DBUser(usuario_id=2, nombre_usuario="admin", email="admin@example.com", contrasena="x", rol="admin")
    with patch("app.services.user_service.revoke_token"):
        result = delete_user(db_user.usuario_id, db, admin_user)
        assert result["message"] == "Usuario eliminado con éxito."

def test_delete_user_not_admin(db, db_user):
    db.query().filter().first.return_value = db_user
    user = DBUser(usuario_id=2, nombre_usuario="user", email="user@example.com", contrasena="x", rol="user")
    with pytest.raises(HTTPException):
        delete_user(db_user.usuario_id, db, user)

def test_delete_user_not_found(db):
    db.query().filter().first.return_value = None
    admin_user = DBUser(usuario_id=2, nombre_usuario="admin", email="admin@example.com", contrasena="x", rol="admin")
    with pytest.raises(HTTPException):
        delete_user(999, db, admin_user)

@patch("app.services.user_service.key_service")
def test_create_refresh_token_success(mock_key_service, db):
    mock_key_service.get_private_key.return_value = "secret"
    with patch("app.services.user_service.jwt.encode", return_value="refresh_token"):
        db.add = MagicMock()
        db.commit = MagicMock()
        result = create_refresh_token(1, db)
        assert result == "refresh_token"

@patch("app.services.user_service.key_service")
def test_create_refresh_token_error(mock_key_service, db):
    mock_key_service.get_private_key.side_effect = Exception("fail")
    db.rollback = MagicMock()
    with pytest.raises(HTTPException):
        create_refresh_token(1, db)


@patch("app.services.user_service.key_service")
def test_verify_refresh_token_no_kid(mock_key_service, db):
    with patch("app.services.user_service.jwt.get_unverified_header", return_value={}):
        with pytest.raises(HTTPException):
            verify_refresh_token("token", db)

@patch("app.services.user_service.key_service")
def test_verify_refresh_token_no_public_key(mock_key_service, db):
    mock_key_service.get_key_by_kid.return_value = None
    with patch("app.services.user_service.jwt.get_unverified_header", return_value={"kid": "kid1"}):
        with pytest.raises(HTTPException):
            verify_refresh_token("token", db)

@patch("app.services.user_service.key_service")
def test_verify_refresh_token_wrong_type(mock_key_service, db):
    mock_key_service.get_key_by_kid.return_value = "public"
    with patch("app.services.user_service.jwt.get_unverified_header", return_value={"kid": "kid1"}), \
         patch("app.services.user_service.jwt.decode", return_value={"type": "access"}):
        with pytest.raises(HTTPException):
            verify_refresh_token("token", db)

@patch("app.services.user_service.key_service")
def test_verify_refresh_token_revoked(mock_key_service, db):
    mock_key_service.get_key_by_kid.return_value = "public"
    with patch("app.services.user_service.jwt.get_unverified_header", return_value={"kid": "kid1"}), \
         patch("app.services.user_service.jwt.decode", return_value={"type": "refresh", "jti": "jti1"}):
        db.query().filter().first.return_value = None
        with pytest.raises(HTTPException):
            verify_refresh_token("token", db)

@patch("app.services.user_service.key_service")
def test_verify_refresh_token_expired(mock_key_service, db):
    mock_key_service.get_key_by_kid.return_value = "public"
    with patch("app.services.user_service.jwt.get_unverified_header", return_value={"kid": "kid1"}), \
         patch("app.services.user_service.jwt.decode", return_value={"type": "refresh", "jti": "jti1"}):
        db.query().filter().first.return_value = MagicMock(expires_at=datetime.utcnow() - timedelta(days=1), is_revoked=False)
        with pytest.raises(HTTPException):
            verify_refresh_token("token", db)

@patch("app.services.user_service.redis_service")
def test_revoke_token_success(mock_redis_service, db):
    mock_redis_service.is_token_blacklisted.return_value = False
    mock_redis_service.add_to_blacklist.return_value = True
    db.query().filter().first.return_value = MagicMock()
    db.commit = MagicMock()
    revoke_token("jti1", "refresh", "admin", "test", db)

@patch("app.services.user_service.redis_service")
def test_revoke_token_already_revoked(mock_redis_service, db):
    mock_redis_service.is_token_blacklisted.return_value = True
    revoke_token("jti1", "refresh", "admin", "test", db)

@patch("app.services.user_service.redis_service")
def test_revoke_token_error(mock_redis_service, db):
    mock_redis_service.is_token_blacklisted.return_value = False
    mock_redis_service.add_to_blacklist.return_value = False
    db.rollback = MagicMock()
    with pytest.raises(HTTPException):
        revoke_token("jti1", "refresh", "admin", "test", db)



def test_is_token_blacklisted_false(db):
    db.query().filter().first.return_value = None
    assert not is_token_blacklisted("jti1", db)

@patch("app.services.user_service.redis_service")
def test_get_blacklist_entries_success(mock_redis_service, db):
    mock_redis_service.get_blacklist_entries.return_value = ["entry1", "entry2"]
    result = get_blacklist_entries(db, limit=2)
    assert result == ["entry1", "entry2"]

@patch("app.services.user_service.redis_service")
def test_get_blacklist_entries_error(mock_redis_service, db):
    mock_redis_service.get_blacklist_entries.side_effect = Exception("fail")
    with pytest.raises(HTTPException):
        get_blacklist_entries(db, limit=2)