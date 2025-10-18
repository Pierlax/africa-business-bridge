from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from ..core.database import get_db
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type
)
from ..core.dependencies import get_current_user
from ..models.user import User
from ..schemas.auth import (
    UserCreate,
    UserResponse,
    Token,
    LoginRequest,
    RefreshTokenRequest,
    ChangePasswordRequest
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuovo utente nella piattaforma.
    
    Args:
        user_data: Dati del nuovo utente
        db: Sessione database
    
    Returns:
        Dati dell'utente creato
    
    Raises:
        HTTPException: Se l'email è già registrata
    """
    # Verifica se l'email è già registrata
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email già registrata"
        )
    
    # Crea il nuovo utente
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        hashed_password=get_password_hash(user_data.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Effettua il login e restituisce i token di accesso.
    
    Args:
        login_data: Credenziali di login
        db: Sessione database
    
    Returns:
        Token di accesso e refresh
    
    Raises:
        HTTPException: Se le credenziali non sono valide
    """
    # Trova l'utente
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password non corretti",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utente non attivo"
        )
    
    # Crea i token
    access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.id, "role": user.role.value})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
def refresh_token(token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Rinnova i token utilizzando il refresh token.
    
    Args:
        token_data: Refresh token
        db: Sessione database
    
    Returns:
        Nuovi token di accesso e refresh
    
    Raises:
        HTTPException: Se il refresh token non è valido
    """
    payload = decode_token(token_data.refresh_token)
    
    # Verifica che sia un refresh token
    if not verify_token_type(payload, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo di token non valido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non valido o non attivo"
        )
    
    # Crea nuovi token
    access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.id, "role": user.role.value})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Restituisce le informazioni dell'utente corrente.
    
    Args:
        current_user: Utente corrente (da dependency)
    
    Returns:
        Informazioni dell'utente
    """
    return current_user


@router.post("/change-password")
def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambia la password dell'utente corrente.
    
    Args:
        password_data: Vecchia e nuova password
        current_user: Utente corrente
        db: Sessione database
    
    Returns:
        Messaggio di conferma
    
    Raises:
        HTTPException: Se la vecchia password non è corretta
    """
    # Verifica la vecchia password
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password corrente non corretta"
        )
    
    # Aggiorna la password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password aggiornata con successo"}


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Effettua il logout (lato client dovrebbe eliminare i token).
    
    Args:
        current_user: Utente corrente
    
    Returns:
        Messaggio di conferma
    """
    return {"message": "Logout effettuato con successo"}

