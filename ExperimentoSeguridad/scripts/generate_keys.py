#!/usr/bin/env python3
"""
Script para generar claves RSA para JWT con RS256
Genera par de claves privada/pública y las guarda en formato PEM
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import os
import json

def generate_rsa_keypair():
    """Genera un par de claves RSA de 2048 bits"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    public_key = private_key.public_key()
    
    return private_key, public_key

def save_private_key(private_key, filename):
    """Guarda la clave privada en formato PEM"""
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    with open(filename, 'wb') as f:
        f.write(pem)

def save_public_key(public_key, filename):
    """Guarda la clave pública en formato PEM"""
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    with open(filename, 'wb') as f:
        f.write(pem)

def create_jwks(public_key, kid="default"):
    """Crea un JWKS (JSON Web Key Set) con la clave pública"""
    # Convertir la clave pública a formato JWK
    public_numbers = public_key.public_numbers()
    
    # Calcular el exponente en base64url
    import base64
    e = base64.urlsafe_b64encode(public_numbers.e.to_bytes(3, 'big')).decode('utf-8').rstrip('=')
    
    # Calcular el módulo en base64url
    n_bytes = public_numbers.n.to_bytes(256, 'big')  # 2048 bits = 256 bytes
    n = base64.urlsafe_b64encode(n_bytes).decode('utf-8').rstrip('=')
    
    jwks = {
        "keys": [
            {
                "kty": "RSA",
                "kid": kid,
                "use": "sig",
                "alg": "RS256",
                "n": n,
                "e": e
            }
        ]
    }
    
    return jwks

def main():
    """Función principal"""
    print("🔑 Generando claves RSA para JWT RS256...")
    
    # Crear directorio de claves si no existe
    os.makedirs("keys", exist_ok=True)
    
    # Generar claves
    private_key, public_key = generate_rsa_keypair()
    
    # Guardar claves
    save_private_key(private_key, "keys/private_key.pem")
    save_public_key(public_key, "keys/public_key.pem")
    
    # Crear JWKS
    jwks = create_jwks(public_key, "default")
    
    # Guardar JWKS
    with open("keys/jwks.json", "w") as f:
        json.dump(jwks, f, indent=2)
    
    print("✅ Claves generadas exitosamente:")
    print("   - keys/private_key.pem (clave privada)")
    print("   - keys/public_key.pem (clave pública)")
    print("   - keys/jwks.json (JWKS para validación)")
    
    # Mostrar información de la clave
    print(f"\n📋 Información de la clave:")
    print(f"   - Algoritmo: RS256")
    print(f"   - Tamaño: 2048 bits")
    print(f"   - Kid: default")
    print(f"   - Uso: firma (sig)")

if __name__ == "__main__":
    main()
