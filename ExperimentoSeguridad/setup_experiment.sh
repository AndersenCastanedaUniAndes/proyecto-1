#!/bin/bash

# Script de configuración para el experimento de seguridad JWT + RBAC
# Título: Disponibilidad y resiliencia de validación JWT + RBAC bajo carga y fallas de infraestructura

set -e

echo "🚀 Configurando experimento de seguridad JWT + RBAC"
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar prerrequisitos
print_status "Verificando prerrequisitos..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado. Instalar Docker primero."
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado. Instalar Docker Compose primero."
    exit 1
fi

# Verificar Python (para tests locales)
if ! command -v python3 &> /dev/null; then
    print_warning "Python3 no encontrado. Los tests locales no funcionarán."
fi

print_success "Prerrequisitos verificados"

# Crear directorios necesarios
print_status "Creando directorios necesarios..."
mkdir -p keys
mkdir -p grafana/provisioning/datasources
mkdir -p grafana/provisioning/dashboards
mkdir -p grafana/dashboards
print_success "Directorios creados"

# Generar claves RSA iniciales si no existen
print_status "Generando claves RSA iniciales..."
if [ ! -f "keys/key-1.json" ]; then
    print_status "Generando par de claves RSA inicial..."
    python3 -c "
import os
import json
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Generar clave privada RSA
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Obtener clave pública
public_key = private_key.public_key()

# Serializar claves a PEM
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
).decode('utf-8')

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode('utf-8')

# Crear JWK
public_numbers = public_key.public_numbers()
def int_to_base64url(value):
    import base64
    byte_length = (value.bit_length() + 7) // 8
    value_bytes = value.to_bytes(byte_length, 'big')
    return base64.urlsafe_b64encode(value_bytes).decode('utf-8').rstrip('=')

jwk = {
    'kty': 'RSA',
    'kid': 'key-1',
    'use': 'sig',
    'alg': 'RS256',
    'n': int_to_base64url(public_numbers.n),
    'e': int_to_base64url(public_numbers.e)
}

# Datos de la clave
key_data = {
    'kid': 'key-1',
    'private_key_pem': private_pem,
    'public_key_pem': public_pem,
    'jwk': jwk,
    'created_at': datetime.utcnow().isoformat(),
    'expires_at': (datetime.utcnow() + timedelta(days=365)).isoformat()
}

# Guardar en archivo
with open('keys/key-1.json', 'w') as f:
    json.dump(key_data, f, indent=2)

print('Clave generada exitosamente')
"
    print_success "Clave RSA inicial generada"
else
    print_success "Clave RSA inicial ya existe"
fi

# Instalar dependencias Python (opcional)
if command -v pip3 &> /dev/null; then
    print_status "Instalando dependencias Python..."
    pip3 install -r requirements.txt > /dev/null 2>&1 || print_warning "Error instalando dependencias Python"
    print_success "Dependencias Python instaladas"
fi

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    print_status "Creando archivo .env..."
    cat > .env << EOF
# Configuración del experimento de seguridad
DATABASE_URL=postgresql://postgres:postgres123@postgres:5432/experimento_seguridad
REDIS_URL=redis://redis:6379/0
JWT_ISS=experimento-seguridad
JWT_AUD=api-users
ACTIVE_KID=key-1
PROMETHEUS_ENABLED=true
EOF
    print_success "Archivo .env creado"
fi

# Verificar que Docker esté ejecutándose
print_status "Verificando que Docker esté ejecutándose..."
if ! docker info &> /dev/null; then
    print_error "Docker no está ejecutándose. Iniciar Docker primero."
    exit 1
fi
print_success "Docker está ejecutándose"

# Levantar servicios
print_status "Levantando servicios con Docker Compose..."
docker-compose up -d

# Esperar a que los servicios estén listos
print_status "Esperando a que los servicios estén listos..."
sleep 30

# Verificar estado de los servicios
print_status "Verificando estado de los servicios..."
services=("postgres" "redis" "app" "prometheus" "grafana")
for service in "${services[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        print_success "$service está ejecutándose"
    else
        print_error "$service no está ejecutándose"
    fi
done

# Verificar endpoints
print_status "Verificando endpoints..."

# Health check
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "API health check OK"
else
    print_warning "API health check falló"
fi

# Métricas
if curl -s http://localhost:8000/metrics > /dev/null; then
    print_success "Métricas Prometheus disponibles"
else
    print_warning "Métricas Prometheus no disponibles"
fi

# Prometheus
if curl -s http://localhost:9090/-/healthy > /dev/null; then
    print_success "Prometheus está ejecutándose"
else
    print_warning "Prometheus no está ejecutándose"
fi

# Grafana
if curl -s http://localhost:3000/api/health > /dev/null; then
    print_success "Grafana está ejecutándose"
else
    print_warning "Grafana no está ejecutándose"
fi

# Ejecutar tests básicos
print_status "Ejecutando tests básicos..."
if command -v python3 &> /dev/null; then
    python3 test_experiment.py
    if [ $? -eq 0 ]; then
        print_success "Tests básicos pasaron"
    else
        print_warning "Algunos tests básicos fallaron"
    fi
else
    print_warning "Python3 no disponible, saltando tests"
fi

# Mostrar información de acceso
echo ""
echo "🎉 ¡Configuración completada!"
echo "=============================="
echo ""
echo "📋 Servicios disponibles:"
echo "  • API: http://localhost:8000"
echo "  • Documentación: http://localhost:8000/docs"
echo "  • Métricas: http://localhost:8000/metrics"
echo "  • Prometheus: http://localhost:9090"
echo "  • Grafana: http://localhost:3000 (admin/admin123)"
echo ""
echo "🔧 Comandos útiles:"
echo "  • Ver logs: docker-compose logs -f"
echo "  • Parar servicios: docker-compose down"
echo "  • Reiniciar: docker-compose restart"
echo "  • Ejecutar tests: python3 test_experiment.py"
echo ""
echo "📊 Próximos pasos para el experimento:"
echo "  1. Acceder a Grafana y verificar dashboard"
echo "  2. Ejecutar pruebas de carga"
echo "  3. Simular fallas de Redis"
echo "  4. Probar rotación de claves"
echo "  5. Monitorear métricas en tiempo real"
echo ""
echo "📖 Documentación completa: README_EXPERIMENTO.md"
echo ""

# Mostrar estado final
print_status "Estado final de los servicios:"
docker-compose ps
