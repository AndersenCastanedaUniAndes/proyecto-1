from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Depends
from pydantic import ValidationError
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from app.models.db_models import Base, DBUser, RefreshToken, TokenBlacklist
from app.models.user import UserCreate, UserUpdate
from config.config import DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import secrets
import hashlib

# Configuración de BD
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuración de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependencia para obtener la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear las tablas en la base de datos
def init_db():
    try:
        print("🔧 Creando tablas en la base de datos...")
        print(f"📊 URL de BD: {DATABASE_URL}")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas correctamente")
        
        # Verificar que las tablas existen
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Tablas disponibles: {tables}")
        
    except Exception as e:
        print(f"❌ Error al crear tablas: {str(e)}")
        raise e

# Manejo de contraseñas
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Crear token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        
        to_encode.update({"exp": expire})
        #print("-----222222222------")
        #print(jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM))

        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el token: {str(e)}")



# Obtener usuario autenticado
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
       
    credentials_exception = HTTPException(
        status_code=401,
        detail="Credenciales inválidas o token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verificar que es un access token
        if payload.get("type") != "access":
            raise credentials_exception

        # Verificar si el token está en la blacklist
        jti = payload.get("jti")
        if jti and is_token_blacklisted(jti, db):
            raise HTTPException(
                status_code=401,
                detail="Token revocado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(DBUser).filter(DBUser.email == email).first()
    
    if user is None:
        raise credentials_exception
    return user

# CRUD
def create_user(user: UserCreate, db: Session):
    try:
        if not all([user.nombre_usuario, user.email, user.contrasena, user.rol]):
            raise HTTPException(status_code=422, detail="Faltan campos obligatorios.")

        existing_user = db.query(DBUser).filter(DBUser.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="El correo ya está registrado.")

        db_user = DBUser(
            nombre_usuario=user.nombre_usuario,
            email=user.email,
            contrasena=hash_password(user.contrasena),
            rol=user.rol
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Error de validación: {e.errors()}")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")

def login_user(email: str, password: str, db: Session):
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user or not verify_password(password, user.contrasena):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    # Crear access token con JTI
    jti = generate_jti()
    access_token = create_access_token(data={
        "sub": user.email,
        "jti": jti,
        "role": user.rol,
        "type": "access"
    })
    
    # Crear refresh token
    refresh_token = create_refresh_token(user.usuario_id, db)
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

def get_user(user_id: int, db: Session, current_user: DBUser):
    try:
        user = db.query(DBUser).filter(DBUser.usuario_id == user_id).first()
        print("-----3333333333------")
        print(user)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        return user
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")

def update_user(user_id: int, user: UserUpdate, db: Session, current_user: DBUser):
    try:
        if not any([user.nombre_usuario, user.email, user.contrasena, user.rol]):
            raise HTTPException(status_code=422, detail="Debe proporcionar al menos un campo para actualizar.")

        db_user = db.query(DBUser).filter(DBUser.usuario_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        if user.nombre_usuario is not None:
            db_user.nombre_usuario = user.nombre_usuario
        if user.email is not None:
            db_user.email = user.email
        if user.contrasena is not None:
            db_user.contrasena = hash_password(user.contrasena)
        if user.rol is not None:
            db_user.rol = user.rol

        db.commit()
        db.refresh(db_user)
        return db_user

    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Error de validación: {e.errors()}")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar usuario: {str(e)}")

def delete_user(user_id: int, db: Session, current_user: DBUser):
    try:
        if current_user.rol != "admin":
            raise HTTPException(status_code=403, detail="No tiene permisos para eliminar usuarios.")

        db_user = db.query(DBUser).filter(DBUser.usuario_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        # Primero, revocar todos los refresh tokens del usuario antes de eliminarlo
        refresh_tokens = db.query(RefreshToken).filter(RefreshToken.user_id == user_id).all()
        for token in refresh_tokens:
            # Agregar a la blacklist
            revoke_token(token.jti, "refresh", current_user.email, "Usuario eliminado", db)

        # Eliminar el usuario (los refresh tokens se eliminarán automáticamente por cascade)
        db.delete(db_user)
        db.commit()
        return {"message": "Usuario eliminado con éxito."}

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuario: {str(e)}")

# Funciones para refresh tokens y revocación
def generate_jti():
    """Genera un JWT ID único"""
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    """Genera hash del token para almacenamiento seguro"""
    return hashlib.sha256(token.encode()).hexdigest()

def create_refresh_token(user_id: int, db: Session) -> str:
    """Crea un refresh token y lo almacena en la base de datos"""
    try:
        # Generar JTI único
        jti = generate_jti()
        
        # Crear fechas de expiración
        expires_at = datetime.utcnow() + timedelta(days=7)  # Refresh token válido por 7 días
        
        # Crear payload del refresh token
        refresh_payload = {
            "sub": str(user_id),
            "jti": jti,
            "type": "refresh",
            "exp": expires_at
        }
        
        # Crear el token
        refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
        
        # Almacenar en la base de datos
        db_refresh_token = RefreshToken(
            jti=jti,
            user_id=user_id,
            token_hash=hash_token(refresh_token),
            expires_at=expires_at,  # Usar el objeto datetime directamente
            is_revoked=False
        )
        
        db.add(db_refresh_token)
        db.commit()
        
        return refresh_token
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear refresh token: {str(e)}")

def verify_refresh_token(token: str, db: Session) -> dict:
    """Verifica un refresh token y retorna el payload si es válido"""
    try:
        # Decodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verificar que es un refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token inválido: no es un refresh token")
        
        # Verificar que no esté revocado
        jti = payload.get("jti")
        db_token = db.query(RefreshToken).filter(
            RefreshToken.jti == jti,
            RefreshToken.is_revoked == False
        ).first()
        
        if not db_token:
            raise HTTPException(status_code=401, detail="Token revocado o inválido")
        
        # Verificar que no haya expirado
        if datetime.utcnow() > db_token.expires_at:
            raise HTTPException(status_code=401, detail="Token expirado")
        
        return payload
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar refresh token: {str(e)}")

def revoke_token(jti: str, token_type: str, revoked_by: str, reason: str, db: Session):
    """Revoca un token agregándolo a la blacklist"""
    try:
        # Verificar si el token ya está en la blacklist
        existing_entry = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
        if existing_entry:
            # El token ya está revocado, no hacer nada
            return
        
        # Crear fechas
        now = datetime.utcnow()
        expires_at = now + timedelta(days=30)  # Mantener en blacklist por 30 días
        
        # Obtener información del token
        if token_type == "refresh":
            db_token = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
            if db_token:
                db_token.is_revoked = True
                db_token.revoked_at = now
                db_token.revoked_by = revoked_by
                db_token.reason = reason
        
        # Agregar a la blacklist
        blacklist_entry = TokenBlacklist(
            jti=jti,
            token_type=token_type,
            expires_at=expires_at,
            revoked_at=now,
            revoked_by=revoked_by,
            reason=reason
        )
        
        db.add(blacklist_entry)
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al revocar token: {str(e)}")

def is_token_blacklisted(jti: str, db: Session) -> bool:
    """Verifica si un token está en la blacklist"""
    try:
        blacklist_entry = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
        return blacklist_entry is not None
    except Exception as e:
        return False

def get_blacklist_entries(db: Session, limit: int = 100):
    """Obtiene las entradas de la blacklist"""
    try:
        entries = db.query(TokenBlacklist).order_by(TokenBlacklist.revoked_at.desc()).limit(limit).all()
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener blacklist: {str(e)}")
