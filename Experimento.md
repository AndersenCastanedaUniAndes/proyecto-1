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