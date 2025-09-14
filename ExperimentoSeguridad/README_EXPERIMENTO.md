# Experimento de Seguridad: Disponibilidad y Resiliencia JWT + RBAC

## Título del Experimento
**Disponibilidad y resiliencia de validación JWT + RBAC bajo carga y fallas de infraestructura**

## Propósito
Medir disponibilidad, latencia y resiliencia del microservicio de seguridad bajo:
- Rotación de claves (kid)
- Caída de Redis (revocación)
- Desfase de reloj ±60s
- Carga concurrente

## Hipótesis Medibles (en segundos)
- **Disponibilidad ≥ 99.5%** durante rotación y fallas
- **Latencia p95 < 1s** y **p99 < 2s** en el middleware de validación
- **≤ 0.5% de errores espurios** durante rotación de claves
- **0 accesos indebidos** con Redis caído (fallback SQL efectivo)
- **Logs/métricas sin exponer secretos**

## Arquitectura

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Cliente   │───▶│   FastAPI    │───▶│ PostgreSQL  │
│  (Postman)  │    │  + JWT RS256 │    │             │
└─────────────┘    └──────────────┘    └─────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │    Redis     │
                   │ (Revocación) │
                   └──────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │  Prometheus  │
                   │   + Grafana  │
                   └──────────────┘
```

## Componentes Implementados

### ✅ Configuración Completa
- **ISS, AUD, ACCESS_TTL_SEC, SKEW_SECONDS=60**
- **ACTIVE_KID, KEYS_DIR, REDIS_URL, DATABASE_URL**
- **RBAC policies** (admin/user roles)

### ✅ KeyStore con Rotación
- Carga todas las claves {kid: public/private} al arrancar
- Permite rotación automática
- Mantiene claves anteriores para compatibilidad

### ✅ JWT RS256 Completo
- **Claims**: sub, role, jti, iat, exp, iss, aud
- **Header**: kid para identificación de clave
- **Validación**: iss/aud/exp/iat con leeway=60s

### ✅ Revocación Redis + Fallback SQL
- **Fail-closed**: Si Redis falla, usa SQL
- **0 accesos indebidos** garantizados
- **Métricas** de estado de Redis

### ✅ RBAC Policy-as-Data
- Políticas en JSON/dict
- Verificación automática de permisos
- Roles: admin (CRUD completo), user (read/update)

### ✅ Middleware con Métricas Prometheus
- **jwt_validation_seconds** (histograma en segundos)
- **jwt_validation_failures_total{reason}** (contador)
- **redis_connection_status** (gauge)

### ✅ Modelos SQLAlchemy
- **User**: usuarios con roles
- **TokenBlacklist**: tokens revocados
- **RefreshToken**: tokens de renovación

## Instalación y Ejecución

### Prerrequisitos
- Docker y Docker Compose
- Python 3.11+ (para desarrollo local)
- Git

### 1. Clonar y Configurar
```bash
cd ExperimentoSeguridad
```

### 2. Ejecutar con Docker Compose
```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f app

# Verificar estado
docker-compose ps
```

### 3. Servicios Disponibles
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Métricas**: http://localhost:8000/metrics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin123)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 4. Desarrollo Local
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/experimento_seguridad"
export REDIS_URL="redis://localhost:6379/0"

# Ejecutar aplicación
uvicorn app.main:app --reload
```

## Pruebas Automáticas

### Ejecutar Tests
```bash
# Todos los tests
pytest tests/ -v

# Test específico
pytest tests/test_login_ok.py -v

# Con cobertura
pytest tests/ --cov=app --cov-report=html
```

### Tests Implementados
1. **test_login_ok.py**: Tokens válidos con kid, role, jti, iss, aud, exp
2. **test_access_roles.py**: GET permitido para admin/user, DELETE solo admin
3. **test_expired_token.py**: 401 para tokens expirados
4. **test_invalid_signature.py**: 401 para firmas inválidas
5. **test_clock_skew.py**: Tolerancia ±60s
6. **test_revocation_redis_down.py**: Fallback SQL con Redis caído
7. **test_key_rotation.py**: Rotación de claves ≤0.5% errores
8. **test_metrics_exposed.py**: /metrics en segundos

## Experimentos de Resiliencia

### 1. Rotación de Claves
```bash
# Crear usuario admin
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"nombre_usuario": "admin", "email": "admin@test.com", "contrasena": "admin123", "rol": "admin"}'

# Login
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@test.com&password=admin123"

# Rotar claves (usar token del login)
curl -X POST "http://localhost:8000/auth/rotate-keys" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Simular Redis Caído
```bash
# Detener Redis
docker-compose stop redis

# Las requests siguen funcionando (fallback SQL)
curl -X GET "http://localhost:8000/users/1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Verificar métricas
curl http://localhost:8000/metrics | grep redis_connection_status
```

### 3. Pruebas de Carga
```bash
# Instalar Apache Bench
sudo apt-get install apache2-utils

# Prueba de carga básica
ab -n 1000 -c 10 -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/users/1

# Ver métricas en tiempo real
watch -n 1 'curl -s http://localhost:8000/metrics | grep jwt_validation_seconds'
```

## Monitoreo y Métricas

### Dashboard Grafana
1. Acceder a http://localhost:3000
2. Login: admin/admin123
3. Dashboard: "Experimento Seguridad JWT + RBAC"

### Métricas Clave
- **jwt_validation_seconds**: Latencia de validación (p95, p99)
- **jwt_validation_failures_total**: Fallos por razón
- **jwt_validation_success_total**: Validaciones exitosas
- **redis_connection_status**: Estado de Redis (1=conectado, 0=desconectado)
- **active_tokens_total**: Tokens activos

### Alertas Recomendadas
```yaml
# Prometheus alerts
- alert: HighJWTValidationLatency
  expr: histogram_quantile(0.95, rate(jwt_validation_seconds_bucket[5m])) > 1
  for: 1m
  labels:
    severity: warning
  annotations:
    summary: "JWT validation p95 latency > 1s"

- alert: RedisDown
  expr: redis_connection_status == 0
  for: 30s
  labels:
    severity: critical
  annotations:
    summary: "Redis is down, using SQL fallback"
```

## Endpoints de la API

### Autenticación
- `POST /token` - Login (obtener tokens)
- `POST /auth/refresh` - Renovar access token
- `POST /auth/revoke` - Revocar token
- `GET /auth/blacklist` - Ver tokens revocados (admin)

### Usuarios
- `POST /users/` - Crear usuario
- `GET /users/{id}` - Obtener usuario
- `PUT /users/{id}` - Actualizar usuario
- `DELETE /users/{id}` - Eliminar usuario (admin)

### Administración
- `POST /auth/rotate-keys` - Rotar claves (admin)
- `GET /.well-known/jwks.json` - Claves públicas JWKS

### Monitoreo
- `GET /health` - Health check
- `GET /metrics` - Métricas Prometheus

## Configuración Avanzada

### Variables de Entorno
```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis
REDIS_URL=redis://host:port/db

# JWT
JWT_ISS=experimento-seguridad
JWT_AUD=api-users
ACTIVE_KID=key-1

# Observabilidad
PROMETHEUS_ENABLED=true
```

### Rotación de Claves
```python
# Rotar manualmente
from app.utils.key_manager import key_manager
new_kid = key_manager.rotate_key()
print(f"Nueva clave: {new_kid}")
```

### Revocación de Tokens
```python
# Revocar token específico
from app.utils.revocation_store import revocation_store
revocation_store.revoke_token(
    jti="token_jti",
    token_type="access",
    revoked_by="admin@test.com",
    reason="Security breach",
    expires_at=datetime.utcnow() + timedelta(hours=1),
    db=db_session
)
```

## Troubleshooting

### Problemas Comunes

1. **Redis no conecta**
   ```bash
   # Verificar estado
   docker-compose logs redis
   
   # Reiniciar Redis
   docker-compose restart redis
   ```

2. **Base de datos no inicializa**
   ```bash
   # Verificar logs
   docker-compose logs postgres
   
   # Recrear volúmenes
   docker-compose down -v
   docker-compose up -d
   ```

3. **Métricas no aparecen**
   ```bash
   # Verificar endpoint
   curl http://localhost:8000/metrics
   
   # Verificar Prometheus
   curl http://localhost:9090/api/v1/targets
   ```

### Logs Importantes
```bash
# Logs de la aplicación
docker-compose logs -f app

# Logs de todos los servicios
docker-compose logs -f

# Logs específicos con timestamps
docker-compose logs -f --timestamps app
```

## Resultados Esperados

### Disponibilidad
- ✅ ≥ 99.5% durante rotación y fallas
- ✅ 0 accesos indebidos con Redis caído
- ✅ Fallback SQL efectivo

### Latencia
- ✅ p95 < 1s en validación JWT
- ✅ p99 < 2s en validación JWT
- ✅ Métricas en segundos (no milisegundos)

### Resiliencia
- ✅ ≤ 0.5% errores espurios durante rotación
- ✅ Tolerancia clock skew ±60s
- ✅ Rotación sin interrupciones

### Observabilidad
- ✅ Métricas Prometheus expuestas
- ✅ Dashboard Grafana funcional
- ✅ Logs sin secretos expuestos

## Contribución

Para contribuir al experimento:

1. Fork el repositorio
2. Crear branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## Licencia

Este proyecto es para fines académicos y de experimentación en seguridad.

---

**Nota**: Este experimento no prueba si "JWT funciona o no", sino atributos de resiliencia y rendimiento académico: disponibilidad, tolerancia a fallas, rotación y métricas observables.
