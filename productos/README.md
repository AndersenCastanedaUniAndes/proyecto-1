# Microservicio Productos — CRUD (FastAPI + PostgreSQL)

## Descripción General
Este microservicio, desarrollado con **Python 3.11** y **FastAPI**, implementa operaciones **CRUD** sobre productos, incluyendo creación, lectura y validación de datos provenientes de archivos **Excel (.xlsx)**. El módulo principal `crud.py` encapsula la lógica de negocio, interactuando con SQLAlchemy y modelos Pydantic.

---

## Tecnologías Principales
- Python 3.11
- FastAPI 0.111.0
- SQLAlchemy 2.0
- Pandas / OpenPyXL / XlsxWriter
- Pytest y Pytest-asyncio
- PostgreSQL 15
- JWT (Python-JOSE) para autenticación

---

## Estructura del Proyecto
```
productos/
│
├─── app/
│   │   main.py                # Punto de entrada FastAPI
│   │
│   ├─── services/
│   │       crud.py            # Lógica CRUD principal
│   │
│   ├─── models/
│   │       models.py          # Definición ORM con SQLAlchemy
│   │
│   ├─── schemas/
│   │       schemas.py         # Modelos Pydantic
│   │
│   └─── utils/
│           security.py        # Seguridad (hash, JWT)
│
├─── tests/
│       test_products.py       # Pruebas unitarias e integración
│
├─── requirements.txt          # Dependencias del proyecto
└─── .github/
    └─── workflows/
            ci.yml             # Pipeline CI/CD (GitHub Actions)
```

---

## Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tuusuario/productos.git
cd productos
```

### 2. Crear un Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### 3. Instalar Dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto:
```bash
DATABASE_URL=postgresql://postgres\:postgres@localhost:5432/products
JWT_SECRET=super-secret-change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## Ejecución del Servicio
Inicia el servidor local:
```bash
uvicorn app.main\:app --reload
```
Abre la documentación interactiva en tu navegador:
```
http://127.0.0.1:8000/docs
```

---

## Funcionalidades Clave en `crud.py`

| Función | Descripción |
|---------|-------------|
| `hash_password` / `verify_password` | Cifra y valida contraseñas. |
| `create_access_token` | Genera tokens JWT de autenticación. |
| `get_paises`, `get_uom`, `get_proveedores`, `get_tipo_almacenamiento` | Devuelven listas ordenadas alfabéticamente. |
| `get_productos_creados` | Lee y valida un archivo Excel con productos. |
| `create_producto` | Inserta un nuevo producto en la base de datos. |

---

## Ejecución de Pruebas
Ejecutar todas las pruebas:
```bash
pytest -v --maxfail=1 --disable-warnings
```
Ver la cobertura de código:
```bash
pytest --cov=app/services/crud.py --cov-report=term-missing
```

---

## CI/CD con GitHub Actions
El workflow ubicado en `.github/workflows/ci.yml`:
- Se ejecuta en cada `push` o `pull_request` a las ramas `main` y `develop`.
- Levanta un contenedor **PostgreSQL 15**.
- Instala dependencias y corre los tests automáticamente.

Prueba el pipeline localmente con [act](https://github.com/nektos/act):
```bash
act pull_request
```

---

## Requisitos del Entorno
- Python ≥ 3.11
- PostgreSQL ≥ 15
- Pip ≥ 25.0
- Docker (opcional, para pruebas locales del CI con `act`)

---

## Autor
**Publio Díaz Páez**  

**Andersen Castañeda**

**Margarita Forero**

Proyecto académico — MISO 2025
Microservicio: *Productos (CRUD con FastAPI y PostgreSQL)*