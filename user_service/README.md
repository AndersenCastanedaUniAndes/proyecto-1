# User Service Microservice

Este microservicio gestiona la administración de usuarios, incluyendo creación, consulta, actualización y eliminación. Forma parte de un sistema basado en microservicios.

## Tabla de Contenidos

- [Características](#características)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [Endpoints](#endpoints)
- [Base de Datos](#base-de-datos)
- [Autenticación](#autenticación)
- [Pruebas](#pruebas)
- [Docker](#docker)
- [Diagramas](#diagramas)
- [Autores](#autores)

---

## Características

- CRUD de usuarios (crear, leer, actualizar, eliminar)
- Autenticación y manejo de contraseñas seguras
- Arquitectura basada en microservicios
- Persistencia con SQLite (puede adaptarse a otros motores)
- Contenerización con Docker

---

## Estructura del Proyecto

```
user_service/
│
├── app/
│   ├── main.py                # Punto de entrada de la aplicación
│   ├── models/                # Modelos de datos y ORM
│   ├── routes/                # Definición de endpoints
│   ├── services/              # Lógica de negocio
│   └── utils/                 # Utilidades (autenticación, etc.)
│
├── config/                    # Configuración de la aplicación
├── Docs/                      # Documentación y diagramas
├── requirements.txt           # Dependencias Python
├── Dockerfile                 # Contenedor Docker
├── users.db                   # Base de datos SQLite
└── .gitignore
```

---

## Instalación

1. **Clona el repositorio:**
   ```sh
   git clone <URL_DEL_REPOSITORIO>
   cd user_service
   ```

2. **Crea un entorno virtual y activa:**
   ```sh
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instala dependencias:**
   ```sh
   pip install -r requirements.txt
   ```

---

## Configuración

- Edita los parámetros en `config/config.py` según tus necesidades (puerto, base de datos, etc).

---

## Ejecución

```sh
python app/main.py
```

El servicio estará disponible en `http://localhost:8000` (o el puerto configurado).

---

## Endpoints

| Método | Endpoint         | Descripción                |
|--------|------------------|----------------------------|
| POST   | /users           | Crear usuario              |
| GET    | /users/{id}      | Obtener usuario por ID     |
| PUT    | /users/{id}      | Actualizar usuario         |
| DELETE | /users/{id}      | Eliminar usuario           |

---

## Base de Datos

- Por defecto utiliza SQLite (`users.db`).
- Los modelos están definidos en `app/models/db_models.py` y `app/models/user.py`.

---

## Autenticación

- Las contraseñas se almacenan de forma segura usando hashing.
- Utilidades de autenticación en `app/utils/auth.py`.

---

## Pruebas

Puedes agregar y ejecutar pruebas unitarias usando `pytest`:

```sh
pip install pytest
pytest
```

---

## Docker

Para construir y correr el servicio en Docker:

```sh
docker build -t user_service .
docker run -p 8000:8000 user_service
```

---

## Diagramas

Los diagramas de clases, componentes y secuencia se encuentran en `Docs/Diagramas/`.

---

## Autores

- [Tu Nombre]
- [Colaboradores]