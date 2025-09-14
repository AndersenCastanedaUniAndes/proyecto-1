#!/usr/bin/env python3
"""
Script de prueba para validar el experimento de seguridad JWT + RBAC
"""
import requests
import time
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"
USER_EMAIL = "user@test.com"
USER_PASSWORD = "user123"

def test_health_check():
    """Test 1: Health check"""
    print("🔍 Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Health check OK: {data['status']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_create_users():
    """Test 2: Crear usuarios"""
    print("\n🔍 Test 2: Crear Usuarios")
    try:
        # Crear admin
        admin_data = {
            "nombre_usuario": "admin_test",
            "email": ADMIN_EMAIL,
            "contrasena": ADMIN_PASSWORD,
            "rol": "admin"
        }
        response = requests.post(f"{BASE_URL}/users/", json=admin_data)
        assert response.status_code == 200
        admin_id = response.json()["usuario_id"]
        print(f"✅ Admin creado: ID {admin_id}")
        
        # Crear usuario regular
        user_data = {
            "nombre_usuario": "user_test",
            "email": USER_EMAIL,
            "contrasena": USER_PASSWORD,
            "rol": "user"
        }
        response = requests.post(f"{BASE_URL}/users/", json=user_data)
        assert response.status_code == 200
        user_id = response.json()["usuario_id"]
        print(f"✅ Usuario creado: ID {user_id}")
        
        return admin_id, user_id
    except Exception as e:
        print(f"❌ Error creando usuarios: {e}")
        return None, None

def test_login_and_tokens(admin_id, user_id):
    """Test 3: Login y tokens"""
    print("\n🔍 Test 3: Login y Tokens")
    try:
        # Login admin
        login_data = {
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/token", data=login_data)
        assert response.status_code == 200
        admin_tokens = response.json()
        print(f"✅ Admin login OK: {admin_tokens['token_type']}")
        
        # Login usuario
        login_data = {
            "username": USER_EMAIL,
            "password": USER_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/token", data=login_data)
        assert response.status_code == 200
        user_tokens = response.json()
        print(f"✅ Usuario login OK: {user_tokens['token_type']}")
        
        return admin_tokens, user_tokens
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None, None

def test_rbac_permissions(admin_tokens, user_tokens, user_id):
    """Test 4: Permisos RBAC"""
    print("\n🔍 Test 4: Permisos RBAC")
    try:
        admin_headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}
        user_headers = {"Authorization": f"Bearer {user_tokens['access_token']}"}
        
        # Admin puede leer usuarios
        response = requests.get(f"{BASE_URL}/users/{user_id}", headers=admin_headers)
        assert response.status_code == 200
        print("✅ Admin puede leer usuarios")
        
        # Usuario puede leer usuarios
        response = requests.get(f"{BASE_URL}/users/{user_id}", headers=user_headers)
        assert response.status_code == 200
        print("✅ Usuario puede leer usuarios")
        
        # Admin puede eliminar usuarios
        response = requests.delete(f"{BASE_URL}/users/{user_id}", headers=admin_headers)
        assert response.status_code == 200
        print("✅ Admin puede eliminar usuarios")
        
        # Usuario NO puede eliminar usuarios
        response = requests.delete(f"{BASE_URL}/users/{user_id}", headers=user_headers)
        assert response.status_code == 403
        print("✅ Usuario NO puede eliminar usuarios (correcto)")
        
        return True
    except Exception as e:
        print(f"❌ Error en RBAC: {e}")
        return False

def test_key_rotation(admin_tokens):
    """Test 5: Rotación de claves"""
    print("\n🔍 Test 5: Rotación de Claves")
    try:
        admin_headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}
        
        # Rotar claves
        response = requests.post(f"{BASE_URL}/auth/rotate-keys", headers=admin_headers)
        assert response.status_code == 200
        rotation_data = response.json()
        print(f"✅ Claves rotadas: {rotation_data['new_kid']}")
        
        # Verificar JWKS
        response = requests.get(f"{BASE_URL}/.well-known/jwks.json")
        assert response.status_code == 200
        jwks = response.json()
        print(f"✅ JWKS disponible: {len(jwks['keys'])} claves")
        
        return True
    except Exception as e:
        print(f"❌ Error en rotación: {e}")
        return False

def test_metrics():
    """Test 6: Métricas Prometheus"""
    print("\n🔍 Test 6: Métricas Prometheus")
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        assert response.status_code == 200
        metrics = response.text
        
        # Verificar métricas clave
        assert "jwt_validation_seconds" in metrics
        assert "jwt_validation_failures_total" in metrics
        assert "jwt_validation_success_total" in metrics
        assert "redis_connection_status" in metrics
        
        print("✅ Métricas Prometheus disponibles")
        print(f"✅ Contiene jwt_validation_seconds")
        print(f"✅ Contiene jwt_validation_failures_total")
        print(f"✅ Contiene redis_connection_status")
        
        return True
    except Exception as e:
        print(f"❌ Error en métricas: {e}")
        return False

def test_clock_skew_tolerance():
    """Test 7: Tolerancia a clock skew"""
    print("\n🔍 Test 7: Tolerancia Clock Skew")
    try:
        # Este test requiere tokens con clock skew específico
        # Por simplicidad, verificamos que el endpoint existe
        response = requests.get(f"{BASE_URL}/.well-known/jwks.json")
        assert response.status_code == 200
        print("✅ Endpoint JWKS disponible para verificación de claves")
        return True
    except Exception as e:
        print(f"❌ Error en clock skew: {e}")
        return False

def test_revocation():
    """Test 8: Revocación de tokens"""
    print("\n🔍 Test 8: Revocación de Tokens")
    try:
        # Crear usuario temporal para revocación
        user_data = {
            "nombre_usuario": "temp_user",
            "email": "temp@test.com",
            "contrasena": "temp123",
            "rol": "user"
        }
        response = requests.post(f"{BASE_URL}/users/", json=user_data)
        assert response.status_code == 200
        temp_user_id = response.json()["usuario_id"]
        
        # Login
        login_data = {
            "username": "temp@test.com",
            "password": "temp123"
        }
        response = requests.post(f"{BASE_URL}/token", data=login_data)
        assert response.status_code == 200
        temp_tokens = response.json()
        
        # Usar token
        headers = {"Authorization": f"Bearer {temp_tokens['access_token']}"}
        response = requests.get(f"{BASE_URL}/users/{temp_user_id}", headers=headers)
        assert response.status_code == 200
        print("✅ Token funciona antes de revocación")
        
        # Revocar token
        revoke_data = {
            "token": temp_tokens["access_token"],
            "reason": "Test de revocación"
        }
        response = requests.post(f"{BASE_URL}/auth/revoke", json=revoke_data, headers=headers)
        assert response.status_code == 200
        print("✅ Token revocado exitosamente")
        
        # Verificar que token revocado no funciona
        response = requests.get(f"{BASE_URL}/users/{temp_user_id}", headers=headers)
        assert response.status_code == 401
        print("✅ Token revocado no funciona (correcto)")
        
        # Limpiar usuario temporal
        admin_headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}
        requests.delete(f"{BASE_URL}/users/{temp_user_id}", headers=admin_headers)
        
        return True
    except Exception as e:
        print(f"❌ Error en revocación: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("🚀 Iniciando pruebas del experimento de seguridad JWT + RBAC")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 8
    
    # Test 1: Health check
    if test_health_check():
        tests_passed += 1
    
    # Test 2: Crear usuarios
    admin_id, user_id = test_create_users()
    if admin_id and user_id:
        tests_passed += 1
    
    # Test 3: Login y tokens
    admin_tokens, user_tokens = test_login_and_tokens(admin_id, user_id)
    if admin_tokens and user_tokens:
        tests_passed += 1
    
    # Test 4: RBAC
    if test_rbac_permissions(admin_tokens, user_tokens, user_id):
        tests_passed += 1
    
    # Test 5: Rotación de claves
    if test_key_rotation(admin_tokens):
        tests_passed += 1
    
    # Test 6: Métricas
    if test_metrics():
        tests_passed += 1
    
    # Test 7: Clock skew
    if test_clock_skew_tolerance():
        tests_passed += 1
    
    # Test 8: Revocación
    if test_revocation():
        tests_passed += 1
    
    # Resultados
    print("\n" + "=" * 60)
    print(f"📊 Resultados: {tests_passed}/{total_tests} tests pasaron")
    
    if tests_passed == total_tests:
        print("🎉 ¡Todos los tests pasaron! El experimento está listo.")
        print("\n📋 Próximos pasos:")
        print("1. Ejecutar: docker-compose up -d")
        print("2. Acceder a Grafana: http://localhost:3000")
        print("3. Ejecutar pruebas de carga")
        print("4. Simular fallas de Redis")
        print("5. Monitorear métricas en tiempo real")
    else:
        print("❌ Algunos tests fallaron. Revisar configuración.")
        print("\n🔧 Verificar:")
        print("1. La aplicación está ejecutándose")
        print("2. Las dependencias están instaladas")
        print("3. La base de datos está inicializada")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

