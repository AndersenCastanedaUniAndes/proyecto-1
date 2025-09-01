# Modelos de arquitectura

## Vista funcional
![Diagrama Funcional](https://github.com/user-attachments/assets/3dfabde4-ae35-4130-8922-8f042ca82b75)

<br>

## Vista despliegue
![MediSupply - Despliegue](https://github.com/user-attachments/assets/9960d224-1558-48fc-b268-57374cb6cceb)

## Vista de información 

### Modelo de Datos 

#### Modelo de despliegue (nodos, réplicas, LB, broker, stores)Debe tener ER con índices (email único), particionamiento (por rango fecha o hash tenant), retención (GDPR/privacidad si aplica).

# Diseño detallado de arquitectura

##  Componente de Inventario
### Vista Funcional
![MediSupply - Vista Funcional Inventario](https://github.com/user-attachments/assets/3b04335e-81a6-41fa-bc5d-3dc8e537a673)


# Diseño del experimento de arquitectura

## E1 Replicación (Escalabilidad) 

### como vamos a hacerlo, Andersen estaba validando replicación y se decidio lo de replicación.  (Experimento 1 - Escalabilidad)

## E2 Seguridad (JWT/roles/refresh/revocación)

### Objetivo

####  Demostrar que solo tokens válidos, no revocados y con rol adecuado acceden a endpoints sensibles, con manejo correcto de expiración y refresh.

### Hipótesis

#### Implementando RS256 con kid (rotación), roles en claims, blacklist por jti, y refresh separado, la tasa de accesos indebidos cae a 0% en pruebas y la validación añade < 5 ms p95.

### Casos a probar (automatizados)

| Caso                               | Descripción                                                                                     |
|------------------------------------|-------------------------------------------------------------------------------------------------|
| Login OK                           | /auth/login → access_token (exp=15m), refresh_token.                                            |
| Acceso con rol                     | GET /users/{id} con role=admin → 200.                                                           |
| Rol insuficiente                   | role=user → 403.                                                                                |
| Token expirado                     |  401                                                                                            |
| Token firma inválida               | (clave equivocada) → 401.                                                                       |
| Token revocado (jti en blacklist)  |  401                                                                                            |
| Refresh OK                         |  /auth/refresh → nuevo access válido.                                                           |
| Refresh inválido/expirado          |  400/401.                                                                                       |
| Clock skew ±60 s                   |  tolerancia configurable.                                                                       |

### Métricas

- p95 de validación del middleware JWT
- % de rechazos correctos
- Tiempo de rotación de claves (si simulan).

### Exito

- 100% de casos pasan; p95 validación < 5 ms.
- No se loguean secretos; headers de seguridad presentes.

### Artefactos

- Middleware JWT (verifica firma con clave pública, kid).
- Revocación simple: set redis o tabla revoked_tokens(jti, expira_en).
- Tests (unitarios + integración) y colección Postman.
- ADR: “Algoritmo y rotación de claves”.

# Refinamiento estrategia de pruebas

## Horas desempeñadas o más componentes a probar etc. Tipos (unit, int, carga, seguridad), horas, riesgos

# Plan de trabajo y tablero

# Video



# Hipótesis
“Si usamos CQRS + Redis Streams podemos asegurar la disponibilidad del sistema de inventario bajo una carga de trabajo alta.”

Grafana

Prueba de lecturas (p95 < 1s, error < 0.5%)
```
$ docker run --rm -i -e BASE=http://host.docker.internal:8000 -v "${PWD}/tests:/scripts" grafana/k6 run /scripts/read.js
```

[Imágenes]

Prueba de escrituras (ack rápido) y lag de proyección
```
$ docker run --rm -i -e BASE=http://host.docker.internal:8000 -v "${PWD}/tests:/scripts" grafana/k6 run /scripts/write_lag.js
```