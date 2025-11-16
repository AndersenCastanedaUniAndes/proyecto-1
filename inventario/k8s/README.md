# Inventario — Kubernetes autoscaling and availability

Estos manifiestos proporcionan una configuración mínima para habilitar autoscaling y mejorar disponibilidad
del microservicio `inventario` en Kubernetes. Están pensados para escenarios de failover y picos de carga.

Archivos incluidos:

- `deployment.yaml` — Deployment y Service para `inventario` (label `app: inventario`).
- `hpa.yaml` — HorizontalPodAutoscaler (autoscaling/v2) basado en CPU.
- `pdb.yaml` — PodDisruptionBudget para mantener al menos 1 pod disponible en interrupciones voluntarias.

Prerequisitos y notas importantes
- Debes instalar `metrics-server` en el clúster para que HPA (por CPU) funcione: https://github.com/kubernetes-sigs/metrics-server
- Para escalar sobre métricas personalizadas (por ejemplo, longitud de una cola Redis, streams, o requests/s) instala:
  - Prometheus + prometheus-adapter (para custom/external metrics) o
  - KEDA (para event-driven scaling — recomendado si usas Redis streams o mensajes).
- Para autoescalar nodos (si necesitas más capacidad de nodo) habilita `cluster-autoscaler` en tu proveedor de nube.

Cómo aplicar

1. Ajusta `deployment.yaml` reemplazando `image: your-registry/inventario:latest` por la imagen real.
2. Aplica los manifiestos:

```powershell
kubectl apply -f .\inventario\k8s\deployment.yaml
kubectl apply -f .\inventario\k8s\pdb.yaml
kubectl apply -f .\inventario\k8s\hpa.yaml
```

Comprobaciones
- Ver estado del HPA:

```powershell
kubectl get hpa inventario-hpa
kubectl describe hpa inventario-hpa
```

- Ver métricas (requiere metrics-server):

```powershell
kubectl top pods -n <namespace>
kubectl top nodes
```

Escenarios de "failover" y recomendaciones
- Mantén `minReplicas` >= 2 si esperas fallos de pod/VM y quieres más tolerancia a fallos.
- Usa `PodDisruptionBudget` para evitar que todos los pods estén indisponibles durante actualizaciones o drains.
- Habilita `readinessProbe` para evitar enviar tráfico a pods que aún no están listos.
- Para cargas muy repentinas (picos) considera:
  - Reducir `scaleUp` cooldowns en el HPA (más agresivo) y/o
  - Habilitar `cluster-autoscaler` (permitirá crear nodos si no hay capacidad en el clúster).

Opcional: ejemplo rápido para escalar por eventos usando KEDA
- Si quieres un escalado por la longitud de una cola Redis/stream, instala KEDA y añade un `ScaledObject` apuntando al Deployment.
- Puedo añadir un ejemplo de `ScaledObject` para Redis Streams o Prometheus-based scaler si me indicas qué fuente de métricas usas.

Si quieres, hago:
- Un `ScaledObject` de KEDA para Redis Streams o RabbitMQ.
- Un `prometheus-adapter` rule y un HPA que use métricas Prometheus.
