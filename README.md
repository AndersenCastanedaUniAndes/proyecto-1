🚀 Flujo de despliegue

Construyes la imagen Docker (docker build -t [tu-registry]/cqrs-api:latest .).

Subes la imagen a tu registry (Docker Hub, ECR, GCR, etc.).

Aplicar manifests:

kubectl apply -f k8s/


Obtienes la IP del Service cqrs-api:

kubectl get svc -n cqrs-demo

Accedes a FastAPI en http://<EXTERNAL-IP>/docs.

<br>
<br>

🔑 Recomendación en producción

Postgres y Redis → usarlos gestionados por el cloud provider (RDS, CloudSQL, Azure Database, Redis Enterprise/ElastiCache).

API y Workers → deploy en Kubernetes (puedes escalar con HPA: kubectl autoscale deployment cqrs-api --cpu-percent=70 --min=3 --max=10).

Manejar secretos con Secrets de Kubernetes en lugar de variables planas.

Usar ConfigMaps para configuración no sensible.

<br>
<br>

🚀 Despliegue con Helm

Crear el chart (si lo copiaste como carpeta):

helm install cqrs-demo ./cqrs-chart


Ver recursos:

kubectl get all -n cqrs-demo


Obtener la IP del servicio de la API:

kubectl get svc -n cqrs-demo


Probar la API en http://<EXTERNAL-IP>/docs.