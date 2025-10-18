from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from .database import get_db
from .security import decode_token, verify_token_type
from ..models.user import User, UserRole

# Security scheme per JWT
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency per ottenere l'utente corrente dal token JWT.
    
    Args:
        credentials: Credenziali HTTP Bearer
        db: Sessione database
    
    Returns:
        Utente corrente
    
    Raises:
        HTTPException: Se il token non è valido o l'utente non esiste
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    # Verifica che sia un access token
    if not verify_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo di token non valido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utente non attivo"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency per ottenere l'utente corrente attivo.
    
    Args:
        current_user: Utente corrente
    
    Returns:
        Utente corrente se attivo
    
    Raises:
        HTTPException: Se l'utente non è attivo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utente non attivo"
        )
    return current_user


def require_role(required_role: UserRole):
    """
    Factory per creare una dependency che verifica il ruolo dell'utente.
    
    Args:
        required_role: Ruolo richiesto
    
    Returns:
        Dependency function
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accesso negato. Ruolo richiesto: {required_role.value}"
            )
        return current_user
    
    return role_checker


def require_roles(*allowed_roles: UserRole):
    """
    Factory per creare una dependency che verifica se l'utente ha uno dei ruoli consentiti.
    
    Args:
        allowed_roles: Ruoli consentiti
    
    Returns:
        Dependency function
    """
    def roles_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accesso negato. Ruoli consentiti: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user
    
    return roles_checker


# Shortcuts per i ruoli più comuni
require_pmi = require_role(UserRole.PMI)
require_partner = require_role(UserRole.PARTNER)
require_admin = require_role(UserRole.ADMIN)

