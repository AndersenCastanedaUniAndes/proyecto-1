#!/usr/bin/env python3
"""
Script para crear un usuario administrador de prueba
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
ADMIN_USER = {
    "nombre_usuario": "admin1",
    "email": "admin1@email.com",
    "contrasena": "Admin123!",
    "rol": "admin"
}

def create_admin_user():
    """Crea un usuario administrador"""
    print("👤 Creando usuario administrador...")
    
    url = f"{BASE_URL}/users/"
    
    try:
        response = requests.post(url, json=ADMIN_USER)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Usuario administrador creado exitosamente!")
            print(f"Usuario: {json.dumps(user_data, indent=2)}")
            return user_data
        else:
            print(f"❌ Error creando usuario: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def main():
    """Función principal"""
    print("🚀 Creando usuario administrador de prueba")
    print("=" * 50)
    
    create_admin_user()
    
    print("\n" + "=" * 50)
    print("🏁 Proceso completado")

if __name__ == "__main__":
    main()
