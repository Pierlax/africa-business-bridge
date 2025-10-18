from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from .config import settings

# Context per l'hashing delle password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se una password corrisponde all'hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera l'hash di una password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT di accesso.
    
    Args:
        data: Dati da includere nel token
        expires_delta: Durata del token (default: da settings)
    
    Returns:
        Token JWT codificato
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Crea un token JWT di refresh.
    
    Args:
        data: Dati da includere nel token
    
    Returns:
        Token JWT codificato
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decodifica e valida un token JWT.
    
    Args:
        token: Token JWT da decodificare
    
    Returns:
        Payload del token
    
    Raises:
        HTTPException: Se il token non è valido
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido o scaduto",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token_type(payload: dict, expected_type: str) -> bool:
    """
    Verifica che il token sia del tipo corretto (access o refresh).
    
    Args:
        payload: Payload del token decodificato
        expected_type: Tipo atteso ("access" o "refresh")
    
    Returns:
        True se il tipo corrisponde
    """
    token_type = payload.get("type")
    return token_type == expected_type

