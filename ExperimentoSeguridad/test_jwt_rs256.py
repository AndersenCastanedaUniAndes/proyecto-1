#!/usr/bin/env python3
"""
Script de prueba para verificar la implementación de JWT RS256 con rotación de claves
"""

import requests
import json
import jwt
from jose import jwt as jose_jwt
import base64

# Configuración
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "admin1@email.com",
    "password": "Admin123!"
}

def test_login():
    """Prueba el endpoint de login"""
    print("🔐 Probando login...")
    
    url = f"{BASE_URL}/token"
    data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login exitoso!")
            print(f"Token Type: {token_data.get('token_type')}")
            print(f"Expires In: {token_data.get('expires_in')} segundos")
            
            # Decodificar token sin verificar para inspeccionar
            access_token = token_data.get('access_token')
            if access_token:
                print("\n🔍 Inspeccionando token...")
                inspect_token(access_token)
                
            return token_data
        else:
            print(f"❌ Error en login: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def inspect_token(token):
    """Inspecciona un token JWT sin verificar"""
    try:
        # Decodificar header
        header = jose_jwt.get_unverified_header(token)
        print(f"Header: {json.dumps(header, indent=2)}")
        
        # Decodificar payload sin verificar
        payload = jose_jwt.decode(token, options={"verify_signature": False})
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Verificar que tiene kid
        if 'kid' in header:
            print(f"✅ Token contiene kid: {header['kid']}")
        else:
            print("❌ Token NO contiene kid")
            
        # Verificar algoritmo
        if header.get('alg') == 'RS256':
            print("✅ Algoritmo correcto: RS256")
        else:
            print(f"❌ Algoritmo incorrecto: {header.get('alg')}")
            
    except Exception as e:
        print(f"❌ Error inspeccionando token: {e}")

def test_jwks():
    """Prueba el endpoint JWKS"""
    print("\n🔑 Probando endpoint JWKS...")
    
    url = f"{BASE_URL}/.well-known/jwks.json"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            jwks = response.json()
            print("✅ JWKS obtenido exitosamente!")
            print(f"JWKS: {json.dumps(jwks, indent=2)}")
            return jwks
        else:
            print(f"❌ Error obteniendo JWKS: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_protected_endpoint(token_data):
    """Prueba un endpoint protegido"""
    print("\n🛡️ Probando endpoint protegido...")
    
    if not token_data:
        print("❌ No hay token para probar")
        return
    
    access_token = token_data.get('access_token')
    if not access_token:
        print("❌ No hay access_token")
        return
    
    url = f"{BASE_URL}/users/1"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Endpoint protegido accesible!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Error accediendo endpoint protegido: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_key_rotation():
    """Prueba la rotación de claves (requiere admin)"""
    print("\n🔄 Probando rotación de claves...")
    
    # Primero necesitamos hacer login como admin
    token_data = test_login()
    if not token_data:
        print("❌ No se pudo obtener token para rotación")
        return
    
    access_token = token_data.get('access_token')
    url = f"{BASE_URL}/auth/rotate-keys"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.post(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Rotación de claves exitosa!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Error en rotación: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas de JWT RS256 con rotación de claves")
    print("=" * 60)
    
    # Prueba 1: Login
    token_data = test_login()
    
    # Prueba 2: JWKS
    test_jwks()
    
    # Prueba 3: Endpoint protegido
    test_protected_endpoint(token_data)
    
    # Prueba 4: Rotación de claves
    test_key_rotation()
    
    print("\n" + "=" * 60)
    print("🏁 Pruebas completadas")

if __name__ == "__main__":
    main()
