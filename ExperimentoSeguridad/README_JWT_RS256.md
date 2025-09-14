# JWT RS256 con Rotación de Claves

Este proyecto implementa autenticación JWT usando RS256 (RSA con clave asimétrica) con soporte para rotación de claves mediante el header `kid`.

## Características

- ✅ **JWT RS256**: Firma asimétrica con claves RSA
- ✅ **Rotación de claves**: Soporte para múltiples claves con `kid`
- ✅ **JWKS**: Endpoint para descubrimiento de claves públicas
- ✅ **RBAC**: Control de acceso basado en roles
- ✅ **Revocación**: Sistema de blacklist para tokens
- ✅ **Refresh tokens**: Renovación automática de tokens

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecutar la aplicación:
```bash
python run.py
```

## Uso

### 1. Crear usuario administrador

```bash
python create_admin_user.py
```

### 2. Obtener token de acceso

```bash
curl --location 'http://localhost:8000/token' \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'username=admin1@email.com' \
  --data-urlencode 'password=Admin123!'
```

### 3. Usar token en endpoints protegidos

```bash
curl --location 'http://localhost:8000/users/1' \
  --header 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

### 4. Obtener claves públicas (JWKS)

```bash
curl --location 'http://localhost:8000/.well-known/jwks.json'
```

### 5. Rotar claves (solo administradores)

```bash
curl --location 'http://localhost:8000/auth/rotate-keys' \
  --header 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

## Estructura de Archivos

```
ExperimentoSeguridad/
├── app/
│   ├── utils/
│   │   ├── key_manager.py      # Gestión de claves RSA
│   │   └── auth.py            # Funciones de autenticación RS256
│   ├── services/
│   │   └── user_service.py    # Servicios de usuario actualizados
│   └── routes/
│       └── user_routes.py     # Rutas con endpoints JWKS y rotación
├── keys/                      # Directorio de claves RSA (generado automáticamente)
├── test_jwt_rs256.py         # Script de pruebas
└── create_admin_user.py      # Script para crear usuario admin
```

## Configuración

### Variables de entorno

- `KEYS_DIRECTORY`: Directorio para almacenar claves (default: "keys")
- `DEFAULT_KID`: ID de clave por defecto (default: "key-1")
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiración de tokens (default: 30)

### Gestión de Claves

Las claves RSA se generan automáticamente en el directorio `keys/` con el formato:
- `{kid}.json`: Archivo JSON con clave privada, pública y metadatos

## Endpoints

### Autenticación
- `POST /token` - Obtener token de acceso
- `POST /auth/refresh` - Renovar token
- `POST /auth/revoke` - Revocar token

### Gestión de Claves
- `GET /.well-known/jwks.json` - Obtener claves públicas
- `POST /auth/rotate-keys` - Rotar claves (admin)

### Usuarios
- `POST /users/` - Crear usuario
- `GET /users/{id}` - Obtener usuario
- `PUT /users/{id}` - Actualizar usuario
- `DELETE /users/{id}` - Eliminar usuario

## Estructura del Token

### Header
```json
{
  "alg": "RS256",
  "kid": "key-1",
  "typ": "JWT"
}
```

### Payload
```json
{
  "sub": "admin1@email.com",
  "jti": "unique-token-id",
  "role": "admin",
  "type": "access",
  "exp": 1234567890
}
```

## Pruebas

Ejecutar el script de pruebas:

```bash
python test_jwt_rs256.py
```

Este script prueba:
- Login y obtención de token
- Verificación de estructura del token
- Acceso a endpoints protegidos
- Endpoint JWKS
- Rotación de claves

## Seguridad

- Las claves privadas se almacenan en archivos locales (no en producción)
- Los tokens incluyen `jti` para revocación
- Soporte para rotación de claves sin interrumpir tokens existentes
- Verificación de firma con claves públicas correspondientes

## Troubleshooting

### Error: "Unable to parse an RSA_JWK from key"
Este error indica que se está pasando un objeto RSA en lugar de una cadena PEM. La implementación actual usa cadenas PEM correctamente.

### Error: "Token inválido: no contiene kid"
Verificar que el token fue creado con la nueva implementación RS256.

### Error: "Clave con kid 'X' no encontrada"
Verificar que la clave existe en el directorio `keys/` o regenerar claves.
