from sqlalchemy import create_engine
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Depends
from typing import List, Optional
from pydantic import ValidationError
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from app.models.db_models import Base, DBUser, PlanVendedor, PlanVenta, DBClient
from app.models.database import engine, get_db
from app.models.user import UserCreate, UserUpdate, ClientCreate
from config.config import DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


# Configuración de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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


def send_forgot_password(email: str, db: Session):
    try:
        # 1️⃣ Buscar el usuario en la base de datos
        user = db.query(DBUser).filter(DBUser.email == email).first()

        # 2️⃣ Si no existe el usuario, no enviamos correo (por seguridad)
        if not user:
            return {"message": "Si el correo existe, se enviarán las instrucciones de recuperación."}

        # 3️⃣ Generar un token JWT temporal para el restablecimiento de contraseña
        expire = timedelta(minutes=15)
        reset_token = create_access_token(
            data={"sub": user.email, "scope": "password_reset"},
            expires_delta=expire
        )

        # 4️⃣ Crear el enlace de restablecimiento
        reset_link = f"https://tuapp.com/reset-password?token={reset_token}"

        # 5️⃣ Preparar el contenido del correo
        subject = "Recuperación de contraseña"
        body = f"""
        Hola {user.nombre_usuario},

        Hemos recibido una solicitud para restablecer tu contraseña.
        Puedes hacerlo usando el siguiente enlace (válido por 15 minutos):

        {reset_link}

        Si no realizaste esta solicitud, ignora este mensaje.

        Saludos,
        El equipo de soporte mediSupply
        """

        # 6️⃣ Configurar el correo
        sender_email = "noreply@tuapp.com"
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # 7️⃣ Enviar el correo usando SMTP (ajusta los valores reales)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = "medisupply1234@gmail.com"
        smtp_password = "kfyihajpvrutgtkt"  # Usa clave de aplicación, no tu contraseña real

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(sender_email, email, msg.as_string())

        return {"message": "Si el correo existe, se enviaron las instrucciones de recuperación."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar correo: {str(e)}")

def crear_plan_venta(periodo, valor_ventas, vendedores_ids, db):
    try:
        # Validar campos obligatorios
        if periodo not in ("mensual", "trimestral", "semestral", "anual"):
            raise HTTPException(status_code=400, detail="Período inválido")
        if valor_ventas < 0:
            raise HTTPException(status_code=400, detail="El valor de ventas no puede ser negativo")
        if not vendedores_ids:
            raise HTTPException(status_code=400, detail="Debe asignar al menos un vendedor")

        # Crear plan de venta
        nuevo_plan = PlanVenta(periodo=periodo, valor_ventas=valor_ventas)
        db.add(nuevo_plan)
        db.flush()  # Para obtener el ID del plan antes del commit

        # Asignar vendedores al plan
        for vendedor_id in vendedores_ids:
            vendedor = db.query(DBUser).filter(DBUser.usuario_id == vendedor_id, DBUser.rol == "vendedor").first()
            if not vendedor:
                raise HTTPException(status_code=404, detail=f"Vendedor con ID {vendedor_id} no encontrado")
            asignacion = PlanVendedor(plan_id=nuevo_plan.id, vendedor_id=vendedor_id)
            db.add(asignacion)

        db.commit()
        db.refresh(nuevo_plan)
        return {"message": "Plan de venta creado exitosamente", "plan_id": nuevo_plan.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear plan: {str(e)}")


def listar_planes_venta(db: Session, current_user: DBUser):
    try:
        planes = db.query(PlanVenta).all()
        resultado = []
        for plan in planes:
            vendedores = [
                {
                    "usuario_id": pv.vendedor.usuario_id,
                    "nombre_usuario": pv.vendedor.nombre_usuario,
                    "email": pv.vendedor.email,
                    "estado": pv.vendedor.estado,
                }
                for pv in plan.vendedores_asignados
            ]
            resultado.append({
                "id": plan.id,
                "periodo": plan.periodo,
                "valor_ventas": float(plan.valor_ventas),
                "fecha_creacion": plan.fecha_creacion,
                "estado": plan.estado,
                "vendedores": vendedores
            })
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar planes: {str(e)}")


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

def actualizar_plan_de_venta(plan_id: int, periodo: Optional[str], valor_ventas: Optional[float], estado: Optional[str], vendedores_ids: Optional[List[int]], db: Session, current_user: DBUser):
    plan = db.query(PlanVenta).filter(PlanVenta.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    try:
        if periodo:
            if periodo not in ("mensual", "trimestral", "semestral", "anual"):
                raise HTTPException(status_code=400, detail="Período inválido")
            plan.periodo = periodo
        if valor_ventas is not None:
            if valor_ventas < 0:
                raise HTTPException(status_code=400, detail="El valor de ventas no puede ser negativo")
            plan.valor_ventas = valor_ventas
        if estado:
            if estado not in ("activo", "completado", "pausado"):
                raise HTTPException(status_code=400, detail="Estado inválido")
            plan.estado = estado
        if vendedores_ids is not None:
            # Borrar asignaciones anteriores
            db.query(PlanVendedor).filter(PlanVendedor.plan_id == plan_id).delete()
            for vendedor_id in vendedores_ids:
                vendedor = db.query(DBUser).filter(DBUser.usuario_id == vendedor_id, DBUser.rol == "vendedor").first()
                if not vendedor:
                    raise HTTPException(status_code=404, detail=f"Vendedor {vendedor_id} no encontrado")
                db.add(PlanVendedor(plan_id=plan.id, vendedor_id=vendedor_id))

        db.commit()
        db.refresh(plan)
        return {"message": "Plan actualizado exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar plan: {str(e)}")

def eliminar_plan_de_venta(plan_id: int, db: Session, current_user: DBUser):
    plan = db.query(PlanVenta).filter(PlanVenta.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    try:
        db.delete(plan)
        db.commit()
        return {"message": "Plan eliminado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar plan: {str(e)}")

def obtener_plan_venta_por_id(plan_id: int, db: Session, current_user: DBUser):
    plan = db.query(PlanVenta).filter(PlanVenta.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    vendedores = [
        {
            "usuario_id": pv.vendedor.usuario_id,
            "nombre_usuario": pv.vendedor.nombre_usuario,
            "email": pv.vendedor.email,
            "estado": pv.vendedor.estado,
        }
        for pv in plan.vendedores_asignados
    ]

    return {
        "id": plan.id,
        "periodo": plan.periodo,
        "valor_ventas": float(plan.valor_ventas),
        "fecha_creacion": plan.fecha_creacion,
        "estado": plan.estado,
        "vendedores": vendedores
    }



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

def create_client(user: ClientCreate, db: Session):
    try:
        if not all([
                user.empresa, user.nombre_usuario, user.email, user.contrasena,
                user.telefono, user.direccion, user.ciudad
            ]):
            raise HTTPException(status_code=422, detail="Faltan campos obligatorios.")

        existing_user = db.query(DBClient).filter(DBClient.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="El correo ya está registrado.")

        db_user = DBClient(
            empresa=user.empresa,
            nombre_usuario=user.nombre_usuario,
            email=user.email,
            contrasena=hash_password(user.contrasena),
            telefono=user.telefono,
            direccion=user.direccion,
            ciudad=user.ciudad,
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
        raise HTTPException(status_code=500, detail=f"Error al crear usuario cliente: {str(e)}")

def get_all_clients(db: Session, skip: int, limit: int):
    try:
        clients: list[DBClient] = db.query(DBClient).offset(skip).limit(limit).all()
        response = [
            {
                "id": client.id,
                "empresa": client.empresa,
                "direccion": client.direccion,
                "telefono": client.telefono,
                "email": client.email,
            }
            for client in clients
        ]

        return response

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los clientes: {str(e)}")


def get_vendedor_clients(vendedor_id: int, db: Session, skip: int, limit: int):
    try:
        clients: list[DBClient] = db.query(DBClient).filter(DBClient.vendedor_id == vendedor_id).offset(skip).limit(limit).all()
        response = [
            {
                "id": client.id,
                "empresa": client.empresa,
                "direccion": client.direccion,
                "telefono": client.telefono,
                "email": client.email,
                "ultima visita": "no registra",
            }
            for client in clients
        ]

        return response

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los clientes: {str(e)}")


def get_client(client_id: int, db: Session):
    try:
        client: DBClient = db.query(DBClient).filter(DBClient.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        return {
            "id": client.id,
            "empresa": client.empresa,
            "direccion": client.direccion,
            "telefono": client.telefono,
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el cliente: {str(e)}")


