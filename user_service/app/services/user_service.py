from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Depends
from typing import List, Optional
from pydantic import ValidationError
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from app.models.db_models import Base, DBUser
from app.models.user import UserCreate, UserUpdate
from config.config import DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

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



def create_vendedor(user: UserCreate, db: Session, current_user: DBUser):
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
            rol="vendedor"
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



def read_vendedores(db: Session, skip: int, limit: int, current_user: DBUser):
    try:
        vendedores = (
            db.query(DBUser)
            .filter(DBUser.rol == "vendedor")  
            .offset(skip)
            .limit(limit)
            .all()
        )
        return vendedores

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los vendedores: {str(e)}")


def read_vendedor(user_id: int, db: Session, current_user: DBUser):
    try:
        user = db.query(DBUser).filter(DBUser.usuario_id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        return user
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")




def update_vendedor(user_id: int, user: UserUpdate, db: Session, current_user: DBUser):
    try:
        #if current_user.rol != "admin" and current_user.usuario_id != user_id:
        #    raise HTTPException(status_code=403, detail="No tienes permisos para modificar otros usuarios")

        #if not any([user.nombre_usuario, user.email, user.contrasena, user.rol]):
        #    raise HTTPException(status_code=422, detail="Debe proporcionar al menos un campo para actualizar.")

        db_user = db.query(DBUser).filter(DBUser.usuario_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        if user.nombre_usuario is not None:
            db_user.nombre_usuario = user.nombre_usuario
        if user.email is not None:
            db_user.email = user.email
        #if user.contrasena is not None:
        #    db_user.contrasena = hash_password(user.contrasena)
        #if user.rol is not None:
        #    db_user.rol = user.rol
        if user.estado is not None:
           db_user.estado = user.estado

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


def delete_vendedor(user_id: int, db: Session, current_user: DBUser):
    try:
        #if current_user.rol != "admin":
        #    raise HTTPException(status_code=403, detail="No tiene permisos para eliminar usuarios.")

        db_user = db.query(DBUser).filter(DBUser.usuario_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        db.delete(db_user)
        db.commit()
        return {"message": "Usuario eliminado con éxito."}

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuario: {str(e)}")


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

        #print("-----11111111-......1------")
        print(payload)

        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    #user = db.query(DBUser).filter(DBUser.contrasena == email).first()
    user = db.query(DBUser).filter(DBUser.email == email).first()
    #print("-----2222222222211111111-......1------"+email)
    print(user)
    
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

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

def get_user(user_id: int, db: Session, current_user: DBUser):
    try:
        user = db.query(DBUser).filter(DBUser.usuario_id == user_id).first()
        #print("-----3333333333------")
        #print(user)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        return user
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")

def update_user(user_id: int, user: UserUpdate, db: Session, current_user: DBUser):
    try:
        if current_user.rol != "admin" and current_user.usuario_id != user_id:
            raise HTTPException(status_code=403, detail="No tienes permisos para modificar otros usuarios")

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

        db.delete(db_user)
        db.commit()
        return {"message": "Usuario eliminado con éxito."}

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuario: {str(e)}")
