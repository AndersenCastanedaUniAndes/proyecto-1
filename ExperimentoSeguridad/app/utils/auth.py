from datetime import datetime, timedelta
import jwt as pyjwt
from passlib.context  import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from config.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ISS, JWT_AUD, SKEW_SECONDS
from app.utils.key_manager import key_manager

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, kid: str = None):
    """Crea un token JWT RS256 con header kid y claims completos (PyJWT)"""
    try:
        to_encode = data.copy()
        now = datetime.utcnow()
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Claims completos
        to_encode.update({
            "exp": expire,
            "iat": now,
            "iss": JWT_ISS,
            "aud": JWT_AUD
        })

        # kid activo por defecto
        if not kid:
            kid = key_manager.get_active_kid()

        # Clave privada PEM (str)
        private_key_pem = key_manager.get_private_key_pem(kid)

        # Headers con kid (incluye typ/alg por claridad)
        headers = {"kid": kid, "typ": "JWT", "alg": "RS256"}

        encoded_jwt = pyjwt.encode(
            to_encode,
            private_key_pem,
            algorithm="RS256",
            headers=headers
        )
        return encoded_jwt

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el token: {str(e)}"
        )

def verify_token(token: str) -> dict:
    """Verifica un token JWT RS256 con validaciones completas (PyJWT)"""
    try:
        # Leer header para obtener kid
        unverified_header = pyjwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="Token inválido: no contiene kid")

        # Clave pública correspondiente
        public_key_pem = key_manager.get_public_key_pem(kid)

        # Decodificar con validaciones completas
        payload = pyjwt.decode(
            token,
            public_key_pem,
            algorithms=["RS256"],
            issuer=JWT_ISS,
            audience=JWT_AUD,
            leeway=SKEW_SECONDS  # Tolerancia de ±60s
        )
        return payload

    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except pyjwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar token: {str(e)}")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Obtiene el usuario actual desde el token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception
