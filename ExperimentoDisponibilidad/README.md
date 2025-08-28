## � CQRS inventario (FastAPI + PostgreSQL + Redis)

Demo educativa de un microservicio que implementa el patrón **CQRS + Event-Driven**: los comandos escriben en el modelo de escritura y publican eventos en Redis; un worker consume esos eventos y actualiza una proyección optimizada para lectura.

---
## 🧱 Arquitectura
Componentes:
1. API (FastAPI) – Endpoints de comandos y queries.
2. PostgreSQL – Modelo de escritura (`inventario`, `lineas_inventario`) y proyección (`inventario_resumen`).
3. Redis Pub/Sub – Canal `events` para propagar eventos de dominio.
4. Worker – `consumers.py` mantiene la tabla de proyección.

Patrón:
```
Cliente → (POST /inventario) → DB (modelo escritura) → Evento InventarioCreado → Worker → Proyección
Cliente → (POST /inventario/{id}/linea) → DB → Evento LineaAgregada → Worker → Incrementa total_items
Cliente → (GET /inventario) → Lee sólo de proyección
``` 
Consistencia: **eventual** entre escritura y proyección.

---
## ✅ Endpoints principales
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /inventario | Crea un inventario (total_items=0) |
| POST | /inventario/{id}/linea | Agrega una línea y emite evento |
| DELETE | /inventario/{id} | Elimina inventario |
| GET | /inventario | Lista proyección (inventario_resumen) |
| GET | /inventario/{id} | Proyección + líneas del inventario |

Documentación interactiva: `/docs` (Swagger) o `/redoc`.

---
## 🔧 Variables de entorno
| Variable | Uso | Valor por defecto (dev) |
|----------|-----|-------------------------|
| DATABASE_URL | Cadena conexión PostgreSQL | postgresql://postgres:postgres@localhost:5432/cqrs_db |
| REDIS_URL | Conexión Redis | redis://localhost:6379 |
| LOG_LEVEL | Nivel de log | INFO |

En Docker/K8s se inyectan ya en los manifests / chart.

---
## 🛠️ Ejecución local (sin Docker)
1. Levanta PostgreSQL y Redis (por ejemplo con Docker rápido):
```
docker run -d --name cqrs-pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=cqrs_db -p 5432:5432 postgres:15
docker run -d --name cqrs-redis -p 6379:6379 redis:7
```
2. Crea tablas:
```
psql postgresql://postgres:postgres@localhost:5432/cqrs_db -f schema.sql
```
3. Instala dependencias:
```
pip install -r requirements.txt
```
4. Ejecuta API y Worker (dos terminales):
```
uvicorn app:app --reload
python consumers.py
```

---
## 🐳 Docker / docker-compose
Build & up:
```
docker compose up --build
```
API: http://localhost:8000/docs

---
## ☸️ Kubernetes (manifests simples)
```
kubectl apply -f k8s/
kubectl get svc -n cqrs-demo
```
Accede: `http://<EXTERNAL-IP>/docs`

---
## ⛏️ Helm Chart
```
helm install cqrs-demo ./cqrs-chart
kubectl get all -n cqrs-demo
```
Desinstalar:
```
helm uninstall cqrs-demo -n cqrs-demo
```

Para cambiar imagen o réplicas, edita `values.yaml`.

---
## 🧪 Tests (pendiente)
Sugeridos:
1. Crear inventario y validar proyección tras breve espera.
2. Agregar líneas y verificar incremento de `total_items`.
3. Eliminar inventario y asegurar borrado de proyección.

---
## 🗄️ Esquema (resumen)
```
inventario(id, cliente, fecha_caducidad)
lineas_inventario(id, inventario_id, producto, cantidad)
inventario_resumen(inventario_id, cliente, total_items, fecha_caducidad)
```
Índices añadidos para: `lineas_inventario.inventario_id`, `inventario_resumen(fecha_caducidad DESC)`.

---
## 🔍 Observabilidad (pendiente)
Próximos pasos sugeridos: métricas (Prometheus), tracing (OpenTelemetry), logs estructurados (JSON).

---
## ♻️ Flujo de eventos
| Evento | Emisor | Consumidor | Efecto |
|--------|--------|------------|--------|
| InventarioCreado | API | Worker | Inserta fila en proyección |
| LineaAgregada | API | Worker | Incrementa total_items |
| InventarioEliminado | API | Worker | Borra de proyección |

Canal Redis: `events` (Pub/Sub; sin persistencia ni replay).

---
## 🔒 Consideraciones producción
- Usar Postgres/Redis gestionados (RDS, CloudSQL, Azure, ElastiCache).
- Secrets de K8s / Vault para credenciales.
- Health checks / readiness probes (añadir endpoints /live /ready o confiar en `/docs` no es ideal).
- Sustituir Pub/Sub por Redis Streams, Kafka o RabbitMQ si se requiere durabilidad y relectura.
- Alembic para migraciones en lugar de `schema.sql` directo.

---
## ✅ Mejoras recientes
Implementado:
1. Variables de entorno para DB y Redis.
2. Logging configurable + mensajes en publicación/consumo.
3. Validaciones de entrada (cliente, producto, cantidad > 0).
4. Manejo básico de errores (400 en entradas inválidas).
5. Eliminación de función obsoleta `crear_inventario0`.
6. Índices para rendimiento de consultas.

---
## 🚀 Roadmap sugerido
| Prioridad | Acción |
|-----------|--------|
| Alta | Tests automáticos de dominio |
| Alta | Health & readiness probes |
| Media | Métricas Prometheus |
| Media | Migraciones con Alembic |
| Media | Retries / resiliencia al publicar eventos |
| Baja | Cache de lecturas frecuentes |

---
## 🧾 Licencia
Proyecto de demostración educativa. Ajusta según tus políticas internas.

---
## 🤝 Contribuir
Fork / branch, PR con descripción clara. Añade tests y actualización de README para nuevas features.

---
## 📬 Contacto
Abre un issue para dudas o mejoras.

---
Happy coding! 🎯