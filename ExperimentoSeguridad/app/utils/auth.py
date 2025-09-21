"""
Authentication utilities for JWT RS256 with comprehensive validation.
"""
from datetime import datetime, timedelta
from typing import Dict, Any

import jwt as pyjwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_AUD,
    JWT_ISS,
    SKEW_SECONDS,
)
from app.utils.key_manager import key_manager

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], kid: str = None) -> str:
    """Create JWT RS256 token with kid header and complete claims."""
    try:
        to_encode = data.copy()
        now = datetime.utcnow()
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        # Complete claims
        to_encode.update({
            "exp": expire,
            "iat": now,
            "iss": JWT_ISS,
            "aud": JWT_AUD,
            "type": "access",  # Ensure token type is access
        })

        # Active kid by default
        if not kid:
            kid = key_manager.get_active_kid()

        # Private key PEM (str)
        private_key_pem = key_manager.get_private_key_pem(kid)

        # Headers with kid (includes typ/alg for clarity)
        headers = {"kid": kid, "typ": "JWT", "alg": "RS256"}

        encoded_jwt = pyjwt.encode(
            to_encode,
            private_key_pem,
            algorithm="RS256",
            headers=headers,
        )
        return encoded_jwt

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating token: {str(e)}",
        )


def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT RS256 token with comprehensive validations."""
    try:
        # Read header to get kid
        unverified_header = pyjwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise HTTPException(
                status_code=401, detail="Invalid token: missing kid"
            )

        # Corresponding public key
        public_key_pem = key_manager.get_public_key_pem(kid)

        # Decode with comprehensive validations
        payload = pyjwt.decode(
            token,
            public_key_pem,
            algorithms=["RS256"],
            issuer=JWT_ISS,
            audience=JWT_AUD,
            leeway=SKEW_SECONDS,  # ±60s tolerance
        )

        # Validate token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401, detail="Invalid token: not an access token"
            )

        return payload

    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except pyjwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error verifying token: {str(e)}"
        )


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """Get current user from token with revocation check."""
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

        # Check token revocation using the same function as middleware
        jti = payload.get("jti")
        if jti:
            from app.services.user_service import get_db
            from app.utils.revocation_store import revocation_store

            db = next(get_db())
            try:
                if revocation_store.is_token_revoked(jti, db):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token revoked",
                    )
            finally:
                db.close()

        return email

    except HTTPException:
        raise
    except Exception:
        raise credentials_exception