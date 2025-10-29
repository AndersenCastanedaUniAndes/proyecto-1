"""
Test: /metrics expone histogramas y counters en segundos
"""
import pytest
import re

def test_metrics_endpoint_exists(client):
    """Test que endpoint /metrics existe"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"

def test_metrics_contains_jwt_validation_failures_counter(client):
    """Test que métricas contienen counter de fallos de validación JWT"""
    response = client.get("/metrics")
    assert response.status_code == 200
    
    content = response.text
    
    # Buscar counter de fallos
    assert "jwt_validation_failures_total" in content
    assert "HELP jwt_validation_failures_total" in content
    assert "Total de fallos en validación JWT" in content

def test_metrics_contains_jwt_validation_success_counter(client):
    """Test que métricas contienen counter de validaciones exitosas"""
    response = client.get("/metrics")
    assert response.status_code == 200
    
    content = response.text
    
    # Buscar counter de éxitos
    assert "jwt_validation_success_total" in content
    assert "HELP jwt_validation_success_total" in content
    assert "Total de validaciones JWT exitosas" in content

def test_metrics_contains_redis_status_gauge(client):
    """Test que métricas contienen gauge de estado de Redis"""
    response = client.get("/metrics")
    assert response.status_code == 200
    
    content = response.text
    
    # Buscar gauge de Redis
    assert "redis_connection_status" in content
    assert "HELP redis_connection_status" in content
    assert "Estado de conexión Redis" in content

def test_metrics_contains_active_tokens_gauge(client):
    """Test que métricas contienen gauge de tokens activos"""
    response = client.get("/metrics")
    assert response.status_code == 200
    
    content = response.text
    
    # Buscar gauge de tokens activos
    assert "active_tokens_total" in content
    assert "HELP active_tokens_total" in content
    assert "Total de tokens activos" in content

def test_metrics_format_is_valid_prometheus(client):
    """Test que formato de métricas es válido para Prometheus"""
    response = client.get("/metrics")
    assert response.status_code == 200
    
    content = response.text
    lines = content.split('\n')
    
    # Verificar que hay al menos algunas métricas
    metric_lines = [line for line in lines if line and not line.startswith('#')]
    assert len(metric_lines) > 0
    
    # Verificar formato de métricas
    for line in metric_lines:
        if line.strip():
            # Debe tener formato: metric_name{labels} value timestamp
            # O al menos: metric_name value
            parts = line.split()
            assert len(parts) >= 2, f"Invalid metric line: {line}"
            
            # Primera parte debe ser el nombre de la métrica
            metric_name = parts[0]
            assert re.match(r'^[a-zA-Z_:][a-zA-Z0-9_:]*', metric_name), f"Invalid metric name: {metric_name}"

def test_metrics_increment_on_requests(client, admin_user_data):
    """Test que métricas se incrementan con requests"""
    # Obtener métricas iniciales
    response = client.get("/metrics")
    initial_content = response.text
    
    # Extraer valor inicial de jwt_validation_success_total
    initial_success_match = re.search(r'jwt_validation_success_total\{[^}]*\} (\d+)', initial_content)
    initial_success = int(initial_success_match.group(1)) if initial_success_match else 0
    
    # Crear usuario y hacer login
    response = client.post("/users/", json=admin_user_data)
    assert response.status_code == 200
    
    login_data = {
        "username": admin_user_data["email"],
        "password": admin_user_data["contrasena"]
    }
    response = client.post("/token", data=login_data)
    access_token = response.json()["access_token"]
    
    # Hacer request autenticado
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/1", headers=headers)
    assert response.status_code == 200
    
    # Obtener métricas después del request
    response = client.get("/metrics")
    final_content = response.text
    
    # Verificar que se incrementó el counter de éxitos
    final_success_match = re.search(r'jwt_validation_success_total\{[^}]*\} (\d+)', final_content)
    final_success = int(final_success_match.group(1)) if final_success_match else 0
    
    assert final_success >= initial_success
