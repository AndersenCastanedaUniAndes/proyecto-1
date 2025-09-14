import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import secrets
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

class RSAKeyManager:
    """Gestor de claves RSA con rotación automática"""
    
    def __init__(self, keys_dir: str = "keys", active_kid: str = None):
        self.keys_dir = keys_dir
        self.active_kid = active_kid or "key-1"
        self.keys_cache: Dict[str, Dict] = {}
        self._ensure_keys_directory()
        self._load_or_generate_keys()
    
    def _ensure_keys_directory(self):
        """Asegura que el directorio de claves existe"""
        if not os.path.exists(self.keys_dir):
            os.makedirs(self.keys_dir)
    
    def _load_or_generate_keys(self):
        """Carga claves existentes o genera nuevas si no existen"""
        # Intentar cargar claves existentes
        if self._load_existing_keys():
            return
        
        # Generar nuevas claves si no existen
        self._generate_new_key_pair(self.active_kid)
    
    def _load_existing_keys(self) -> bool:
        """Carga claves existentes desde archivos"""
        try:
            # Buscar archivos de claves existentes
            key_files = [f for f in os.listdir(self.keys_dir) if f.endswith('.json')]
            
            if not key_files:
                return False
            
            for key_file in key_files:
                kid = key_file.replace('.json', '')
                key_path = os.path.join(self.keys_dir, key_file)
                
                with open(key_path, 'r') as f:
                    key_data = json.load(f)
                    self.keys_cache[kid] = key_data
            
            return len(self.keys_cache) > 0
            
        except Exception as e:
            print(f"Error cargando claves existentes: {e}")
            return False
    
    def _generate_new_key_pair(self, kid: str) -> Dict:
        """Genera un nuevo par de claves RSA"""
        try:
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
            
            # Crear JWK para la clave pública
            jwk = self._create_jwk(public_key, kid)
            
            # Datos de la clave
            key_data = {
                "kid": kid,
                "private_key_pem": private_pem,
                "public_key_pem": public_pem,
                "jwk": jwk,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(days=365)).isoformat()
            }
            
            # Guardar en archivo
            key_path = os.path.join(self.keys_dir, f"{kid}.json")
            with open(key_path, 'w') as f:
                json.dump(key_data, f, indent=2)
            
            # Agregar al cache
            self.keys_cache[kid] = key_data
            
            return key_data
            
        except Exception as e:
            raise Exception(f"Error generando par de claves: {e}")
    
    def _create_jwk(self, public_key, kid: str) -> Dict:
        """Crea un JWK (JSON Web Key) para la clave pública"""
        try:
            # Obtener números de la clave pública
            public_numbers = public_key.public_numbers()
            
            # Convertir a base64url
            def int_to_base64url(value):
                import base64
                # Convertir a bytes
                byte_length = (value.bit_length() + 7) // 8
                value_bytes = value.to_bytes(byte_length, 'big')
                # Convertir a base64url
                return base64.urlsafe_b64encode(value_bytes).decode('utf-8').rstrip('=')
            
            return {
                "kty": "RSA",
                "kid": kid,
                "use": "sig",
                "alg": "RS256",
                "n": int_to_base64url(public_numbers.n),
                "e": int_to_base64url(public_numbers.e)
            }
            
        except Exception as e:
            raise Exception(f"Error creando JWK: {e}")
    
    def get_private_key_pem(self, kid: str = None) -> str:
        """Obtiene la clave privada PEM para firmar"""
        kid = kid or self.active_kid
        
        if kid not in self.keys_cache:
            raise Exception(f"Clave con kid '{kid}' no encontrada")
        
        return self.keys_cache[kid]["private_key_pem"]
    
    def get_public_key_pem(self, kid: str) -> str:
        """Obtiene la clave pública PEM para verificar"""
        if kid not in self.keys_cache:
            raise Exception(f"Clave con kid '{kid}' no encontrada")
        
        return self.keys_cache[kid]["public_key_pem"]
    
    def get_jwk(self, kid: str) -> Dict:
        """Obtiene el JWK para una clave específica"""
        if kid not in self.keys_cache:
            raise Exception(f"Clave con kid '{kid}' no encontrada")
        
        return self.keys_cache[kid]["jwk"]
    
    def get_active_kid(self) -> str:
        """Obtiene el kid de la clave activa"""
        return self.active_kid
    
    def get_jwks(self) -> Dict:
        """Obtiene el conjunto de claves públicas (JWKS)"""
        return {
            "keys": [self.get_jwk(kid) for kid in self.keys_cache.keys()]
        }
    
    def rotate_key(self) -> str:
        """Rota la clave activa generando una nueva"""
        # Generar nuevo kid
        new_kid = f"key-{int(datetime.utcnow().timestamp())}"
        
        # Generar nueva clave
        self._generate_new_key_pair(new_kid)
        
        # Actualizar clave activa
        self.active_kid = new_kid
        
        return new_kid
    
    def get_all_kids(self) -> list:
        """Obtiene todos los kids disponibles"""
        return list(self.keys_cache.keys())

# Instancia global del gestor de claves
key_manager = RSAKeyManager()
