"""
Sistema RBAC (Role-Based Access Control) policy-as-data
"""
from typing import Dict, List, Optional
from fastapi import HTTPException, status
from config.config import RBAC_POLICIES

class RBACManager:
    """Gestor de RBAC con políticas basadas en datos"""
    
    def __init__(self, policies: Dict = None):
        self.policies = policies or RBAC_POLICIES
    
    def has_permission(self, role: str, resource: str, action: str) -> bool:
        """
        Verifica si un rol tiene permiso para realizar una acción en un recurso
        
        Args:
            role: Rol del usuario (admin, user, etc.)
            resource: Recurso (users, auth, etc.)
            action: Acción (read, create, update, delete, etc.)
        
        Returns:
            bool: True si tiene permiso, False en caso contrario
        """
        try:
            # Verificar si el rol existe
            if role not in self.policies:
                return False
            
            # Verificar si el recurso existe para el rol
            role_policies = self.policies[role]
            if resource not in role_policies:
                return False
            
            # Verificar si la acción está permitida
            allowed_actions = role_policies[resource]
            return action in allowed_actions
            
        except Exception as e:
            # En caso de error, denegar acceso (fail-closed)
            return False
    
    def check_permission(self, role: str, resource: str, action: str) -> None:
        """
        Verifica permisos y lanza excepción si no tiene acceso
        
        Args:
            role: Rol del usuario
            resource: Recurso
            action: Acción
        
        Raises:
            HTTPException: 403 si no tiene permisos
        """
        if not self.has_permission(role, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol '{role}' no tiene permisos para '{action}' en '{resource}'"
            )
    
    def get_user_permissions(self, role: str) -> Dict[str, List[str]]:
        """
        Obtiene todos los permisos de un rol
        
        Args:
            role: Rol del usuario
        
        Returns:
            Dict con recursos y acciones permitidas
        """
        return self.policies.get(role, {})
    
    def get_all_roles(self) -> List[str]:
        """Obtiene todos los roles disponibles"""
        return list(self.policies.keys())
    
    def add_role_policy(self, role: str, resource: str, actions: List[str]) -> None:
        """
        Agrega una política para un rol
        
        Args:
            role: Rol
            resource: Recurso
            actions: Lista de acciones permitidas
        """
        if role not in self.policies:
            self.policies[role] = {}
        
        self.policies[role][resource] = actions
    
    def remove_role_policy(self, role: str, resource: str) -> None:
        """
        Remueve una política para un rol
        
        Args:
            role: Rol
            resource: Recurso
        """
        if role in self.policies and resource in self.policies[role]:
            del self.policies[role][resource]
    
    def validate_policy_structure(self) -> bool:
        """
        Valida que la estructura de políticas sea correcta
        
        Returns:
            bool: True si la estructura es válida
        """
        try:
            for role, resources in self.policies.items():
                if not isinstance(resources, dict):
                    return False
                
                for resource, actions in resources.items():
                    if not isinstance(actions, list):
                        return False
                    
                    for action in actions:
                        if not isinstance(action, str):
                            return False
            
            return True
            
        except Exception:
            return False

# Instancia global
rbac_manager = RBACManager()

# Decorador para verificar permisos
def require_permission(resource: str, action: str):
    """
    Decorador para verificar permisos en endpoints
    
    Usage:
        @require_permission("users", "read")
        def get_user():
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Obtener el usuario actual del contexto
            # Esto asume que el usuario está disponible en kwargs o args
            current_user = None
            for arg in args:
                if hasattr(arg, 'rol'):
                    current_user = arg
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            # Verificar permisos
            rbac_manager.check_permission(current_user.rol, resource, action)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
