"""
Servicio para manejo de claves RSA y JWKS
Implementa rotación de claves con soporte para kid
"""

import os
import json
from typing import Dict, Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from config.config import PRIVATE_KEY_PATH, PUBLIC_KEY_PATH, JWKS_PATH, KEY_ID

class KeyService:
    """Servicio para manejo de claves RSA y JWKS"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.jwks = None
        self.current_kid = KEY_ID
        self.load_keys()
    
    def load_keys(self):
        """Carga las claves RSA desde archivos"""
        try:
            # Cargar clave privada
            with open(PRIVATE_KEY_PATH, 'rb') as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            
            # Cargar clave pública
            with open(PUBLIC_KEY_PATH, 'rb') as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
            
            # Cargar JWKS
            with open(JWKS_PATH, 'r') as f:
                self.jwks = json.load(f)
            
            print(f"✅ Claves RSA cargadas correctamente (kid: {self.current_kid})")
            
        except FileNotFoundError as e:
            print(f"❌ Error: Archivo de clave no encontrado: {e}")
            print("💡 Ejecuta: python scripts/generate_keys.py")
            raise
        except Exception as e:
            print(f"❌ Error al cargar claves: {e}")
            raise
    
    def get_private_key(self) -> str:
        """Retorna la clave privada actual en formato PEM"""
        if not self.private_key:
            raise ValueError("Clave privada no cargada")
        
        # Convertir a formato PEM
        pem_private = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem_private.decode('utf-8')
    
    def get_public_key(self) -> str:
        """Retorna la clave pública actual en formato PEM"""
        if not self.public_key:
            raise ValueError("Clave pública no cargada")
        
        # Convertir a formato PEM
        pem_public = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem_public.decode('utf-8')
    
    def get_jwks(self) -> Dict:
        """Retorna el JWKS actual"""
        if not self.jwks:
            raise ValueError("JWKS no cargado")
        return self.jwks
    
    def get_current_kid(self) -> str:
        """Retorna el kid actual"""
        return self.current_kid
    
    def rotate_keys(self, new_kid: str = None):
        """Rota las claves RSA (implementación futura)"""
        # TODO: Implementar rotación de claves
        # Por ahora, solo cambiamos el kid
        if new_kid:
            self.current_kid = new_kid
            print(f"🔄 Kid rotado a: {new_kid}")
    
    def get_key_by_kid(self, kid: str) -> Optional[str]:
        """Retorna la clave pública por kid (para validación) en formato PEM"""
        if kid == self.current_kid:
            return self.get_public_key()
        # TODO: Implementar búsqueda en múltiples claves
        return None

# Instancia global del servicio de claves
key_service = KeyService()
