from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import User, UserCreate, UserUpdate, TokenResponse, RefreshTokenRequest, RevokeTokenRequest, BlacklistEntry
from app.models.db_models import DBUser
from app.services.user_service import (
    create_user, 
    get_user, 
    update_user, 
    delete_user, 
    get_db, 
    verify_password, 
    create_access_token,
    get_current_user,
    create_refresh_token,
    verify_refresh_token,
    revoke_token,
    get_blacklist_entries,
    login_user
)
from app.services.key_service import key_service
from app.services.redis_service import redis_service

router = APIRouter()

# Crear usuario (registro)
@router.post("/users/", response_model=User)
def create_user_route(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(user, db)

# Obtener usuario por ID (protegido)
@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    print("-----11111111-......1------")
   
    return get_user(user_id, db,current_user)

# Actualizar usuario por ID (protegido)
@router.put("/users/{user_id}", response_model=User)
def update_user_route(user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    return update_user(user_id, user, db,current_user)

# Eliminar usuario por ID (protegido)
@router.delete("/users/{user_id}")
def delete_user_route(user_id: int, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    return delete_user(user_id, db,current_user)

# Login para obtener token
@router.post("/token", response_model=TokenResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Usar la nueva función de login que incluye refresh token
        token_data = login_user(form_data.username, form_data.password, db)
        return token_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(  
            status_code=500,
            detail=f"Error interno en autenticación: {str(e)}"
        )




# Refresh token endpoint
@router.post("/auth/refresh", response_model=TokenResponse)
def refresh_access_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        # Verificar el refresh token
        payload = verify_refresh_token(refresh_request.refresh_token, db)
        
        # Obtener el usuario
        user_id = int(payload.get("sub"))
        user = db.query(DBUser).filter(DBUser.usuario_id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        # Crear nuevo access token
        from app.services.user_service import generate_jti
        jti = generate_jti()
        access_token = create_access_token(data={
            "sub": user.email,
            "jti": jti,
            "role": user.rol,
            "type": "access"
        })
        
        # Crear nuevo refresh token (rotación)
        new_refresh_token = create_refresh_token(user.usuario_id, db)
        
        # Revocar el refresh token anterior
        old_jti = payload.get("jti")
        revoke_token(old_jti, "refresh", user.email, "Token rotado", db)
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 30 * 60  # 30 minutos
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al refrescar token: {str(e)}")

# Revocar token endpoint
@router.post("/auth/revoke")
def revoke_access_token(
    revoke_request: RevokeTokenRequest,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Decodificar el token para obtener el JTI
        import jwt
        from jwt.exceptions import InvalidTokenError
        from app.services.key_service import key_service
        
        # Obtener el kid del token
        unverified_header = jwt.get_unverified_header(revoke_request.token)
        kid = unverified_header.get("kid")
        
        if not kid:
            raise HTTPException(status_code=400, detail="Token inválido: falta kid")
        
        # Obtener la clave pública correspondiente
        public_key = key_service.get_key_by_kid(kid)
        if not public_key:
            raise HTTPException(status_code=400, detail="Token inválido: kid no encontrado")
        
        payload = jwt.decode(
            revoke_request.token, 
            public_key, 
            algorithms=["RS256"],
            audience="experimento-seguridad",
            issuer="experimento-seguridad"
        )
        jti = payload.get("jti")
        token_type = payload.get("type", "access")
        
        if not jti:
            raise HTTPException(status_code=400, detail="Token inválido: no contiene JTI")
        
        # Revocar el token
        revoke_token(jti, token_type, current_user.email, revoke_request.reason or "Revocado por usuario", db)
        
        return {"message": "Token revocado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al revocar token: {str(e)}")

# Ver blacklist endpoint (solo para admins)
@router.get("/auth/blacklist", response_model=list[BlacklistEntry])
def get_token_blacklist(
    limit: int = 100,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar que el usuario sea admin
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden ver la blacklist")
    
    try:
        entries = get_blacklist_entries(db, limit)
        return entries
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener blacklist: {str(e)}")

# JWKS endpoint (público)
@router.get("/.well-known/jwks.json")
def get_jwks():
    """Endpoint público para obtener las claves públicas (JWKS)"""
    try:
        jwks = key_service.get_jwks()
        return jwks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener JWKS: {str(e)}")

# Estado de Redis endpoint (solo para admins)
@router.get("/auth/redis-status")
def get_redis_status(current_user: DBUser = Depends(get_current_user)):
    """Endpoint para verificar el estado de Redis (solo admin)"""
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden ver el estado de Redis")
    
    try:
        status = redis_service.get_redis_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estado de Redis: {str(e)}")

# Autenticación interna
def authenticate_user(db, email: str, password: str):
    try:
        user = db.query(DBUser).filter(DBUser.email == email).first()
        
        if not user or not verify_password(password, user.contrasena):
            return False
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al autenticar usuario: {str(e)}")
