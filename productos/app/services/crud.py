from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import UploadFile, File,HTTPException, Depends
from pydantic import ValidationError
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.databases import Base
from config.config import DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.orm import Session
from app.models import models, producto
from typing import List, Optional
from datetime import datetime
import pandas as pd 
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


# CRUD básico

def get_producto(db: Session, producto_id: int) -> Optional[models.Producto]:
    return db.query(models.Producto).filter(models.Producto.id == producto_id).first()


def get_producto_by_serial(db: Session, numeroSerial: str) -> Optional[models.Producto]:
    return db.query(models.Producto).filter(models.Producto.numeroSerial == numeroSerial).first()


def get_productos(db: Session, skip: int = 0, limit: int = 100) -> List[models.Producto]:
    return db.query(models.Producto).offset(skip).limit(limit).all()


from typing import List

def get_paises() -> List[str]:
    """
    Retorna una lista completa de países ordenada alfabéticamente.
    """
    paises = [
        "Afganistán", "Albania", "Alemania", "Andorra", "Angola", "Antigua y Barbuda", "Arabia Saudita",
        "Argelia", "Argentina", "Armenia", "Australia", "Austria", "Azerbaiyán", "Bahamas", "Bangladés",
        "Barbados", "Baréin", "Bélgica", "Belice", "Benín", "Bielorrusia", "Birmania", "Bolivia", 
        "Bosnia y Herzegovina", "Botsuana", "Brasil", "Brunéi", "Bulgaria", "Burkina Faso", "Burundi",
        "Bután", "Cabo Verde", "Camboya", "Camerún", "Canadá", "Catar", "Chad", "Chile", "China", "Chipre",
        "Colombia", "Comoras", "Congo", "Corea del Norte", "Corea del Sur", "Costa de Marfil", "Costa Rica",
        "Croacia", "Cuba", "Dinamarca", "Dominica", "Ecuador", "Egipto", "El Salvador", "Emiratos Árabes Unidos",
        "Eritrea", "Eslovaquia", "Eslovenia", "España", "Estados Unidos", "Estonia", "Etiopía", "Filipinas",
        "Finlandia", "Fiyi", "Francia", "Gabón", "Gambia", "Georgia", "Ghana", "Granada", "Grecia", "Guatemala",
        "Guinea", "Guinea-Bisáu", "Guinea Ecuatorial", "Guyana", "Haití", "Honduras", "Hungría", "India", 
        "Indonesia", "Irak", "Irán", "Irlanda", "Islandia", "Islas Marshall", "Islas Salomón", "Israel", 
        "Italia", "Jamaica", "Japón", "Jordania", "Kazajistán", "Kenia", "Kirguistán", "Kiribati", "Kuwait",
        "Laos", "Lesoto", "Letonia", "Líbano", "Liberia", "Libia", "Liechtenstein", "Lituania", "Luxemburgo",
        "Macedonia del Norte", "Madagascar", "Malasia", "Malaui", "Maldivas", "Malí", "Malta", "Marruecos",
        "Mauricio", "Mauritania", "México", "Micronesia", "Moldavia", "Mónaco", "Mongolia", "Montenegro",
        "Mozambique", "Namibia", "Nauru", "Nepal", "Nicaragua", "Níger", "Nigeria", "Noruega", "Nueva Zelanda",
        "Omán", "Países Bajos", "Pakistán", "Palaos", "Panamá", "Papúa Nueva Guinea", "Paraguay", "Perú",
        "Polonia", "Portugal", "Reino Unido", "República Centroafricana", "República Checa",
        "República del Congo", "República Democrática del Congo", "República Dominicana", "Ruanda",
        "Rumania", "Rusia", "Samoa", "San Cristóbal y Nieves", "San Marino", "San Vicente y las Granadinas",
        "Santa Lucía", "Santo Tomé y Príncipe", "Senegal", "Serbia", "Seychelles", "Sierra Leona", "Singapur",
        "Siria", "Somalia", "Sri Lanka", "Suazilandia", "Sudáfrica", "Sudán", "Sudán del Sur", "Suecia",
        "Suiza", "Surinam", "Tailandia", "Tanzania", "Tayikistán", "Timor Oriental", "Togo", "Tonga",
        "Trinidad y Tobago", "Túnez", "Turkmenistán", "Turquía", "Tuvalu", "Ucrania", "Uganda", "Uruguay",
        "Uzbekistán", "Vanuatu", "Vaticano", "Venezuela", "Vietnam", "Yemen", "Yibuti", "Zambia", "Zimbabue"
    ]
    
    # Ordena la lista alfabéticamente ignorando mayúsculas y tildes
    return sorted(paises, key=lambda p: p.lower())

def get_uom() -> List[str]:
    """
    Retorna una lista completa de uom.
    """
    paises = ["unidad" , "paquete" , "caja" , "pallet"]
    
    # Ordena la lista alfabéticamente ignorando mayúsculas y tildes
    return sorted(paises, key=lambda p: p.lower())

def get_tipo_almacenamiento() -> List[str]:
    """
    Retorna una lista completa de tipos de almacenamiento.
    """
    paises = ["unidad" , "paquete" , "caja" , "pallet"]
    
    # Ordena la lista alfabéticamente ignorando mayúsculas y tildes
    return sorted(paises, key=lambda p: p.lower())


async def get_productos_creados(file: UploadFile = File(...),  db: Session = Depends(get_db)):
    """
    Endpoint para cargar un archivo Excel con productos y guardarlos en la BD.
    """

    # Validar extensión
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="El archivo debe ser un Excel (.xlsx o .xls)")

    try:
        # Leer el archivo Excel con pandas
        contents = await file.read()
        df = pd.read_excel(contents)

        # Validar columnas obligatorias
        columnas_requeridas = [
            "nombre", "lote", "numeroSerial", "proveedor",
            "precioUnidad", "precioTotal", "paisOrigen",
            "uom", "cantidad", "tipoAlmacenamiento",
            "temperaturaMin", "temperaturaMax"
        ]

        for col in columnas_requeridas:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Columna faltante en el Excel: {col}")

        productos_creados = []
        for _, row in df.iterrows():
            # Evitar duplicados por numeroSerial
            if get_producto_by_serial(db, str(row["numeroSerial"])):
                continue  # puedes cambiar por raise si prefieres abortar

            producto_data = models.Producto(
                nombre=row["nombre"],
                lote=row["lote"],
                numeroSerial=str(row["numeroSerial"]),
                proveedor=row["proveedor"],
                precioUnidad=float(row["precioUnidad"]),
                precioTotal=float(row["precioTotal"]),
                paisOrigen=row["paisOrigen"],
                uom=row["uom"],
                cantidad=int(row["cantidad"]),
                tipoAlmacenamiento=row["tipoAlmacenamiento"],
                temperaturaMin=float(row["temperaturaMin"]) if not pd.isna(row["temperaturaMin"]) else None,
                temperaturaMax=float(row["temperaturaMax"]) if not pd.isna(row["temperaturaMax"]) else None
            )

            nuevo_producto = create_producto(db, producto_data)
            productos_creados.append(nuevo_producto)

        return {"mensaje": f"{len(productos_creados)} productos cargados exitosamente."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando el archivo: {str(e)}")





def create_producto(db: Session, producto) -> models.Producto:
    db_obj = models.Producto(
        nombre=producto.nombre,
        lote=producto.lote,
        numeroSerial=producto.numeroSerial,
        proveedor=producto.proveedor,
        precioUnidad=producto.precioUnidad,
        precioTotal=producto.precioTotal,
        paisOrigen=producto.paisOrigen,
        uom=producto.uom,
        cantidad=producto.cantidad,
        tipoAlmacenamiento=producto.tipoAlmacenamiento,
        temperaturaMin=producto.temperaturaMin,
        temperaturaMax=producto.temperaturaMax,
        fechaCreacion = producto.fechaCreacion if hasattr(producto, 'fechaCreacion') else __import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_producto(db: Session, db_producto: models.Producto, producto_in: models.Producto) -> models.Producto:
    for field, value in producto_in.dict().items():
        setattr(db_producto, field, value)
    db.commit()
    db.refresh(db_producto)
    return db_producto


def delete_producto(db: Session, db_producto: models.Producto):
    db.delete(db_producto)
    db.commit()
    return

