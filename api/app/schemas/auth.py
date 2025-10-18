from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from ..models.user import UserRole


class UserBase(BaseModel):
    """Schema base per gli utenti"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role: UserRole


class UserCreate(UserBase):
    """Schema per la creazione di un nuovo utente"""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Valida che la password sia sufficientemente forte"""
        if not any(char.isdigit() for char in v):
            raise ValueError('La password deve contenere almeno un numero')
        if not any(char.isupper() for char in v):
            raise ValueError('La password deve contenere almeno una lettera maiuscola')
        if not any(char.islower() for char in v):
            raise ValueError('La password deve contenere almeno una lettera minuscola')
        return v


class UserUpdate(BaseModel):
    """Schema per l'aggiornamento di un utente"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserInDB(UserBase):
    """Schema per l'utente nel database"""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """Schema per la risposta con i dati utente"""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema per la risposta del token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema per il payload del token"""
    sub: int  # user_id
    role: str
    exp: Optional[datetime] = None


class LoginRequest(BaseModel):
    """Schema per la richiesta di login"""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Schema per la richiesta di refresh del token"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Schema per la richiesta di reset password"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema per la conferma del reset password"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class ChangePasswordRequest(BaseModel):
    """Schema per il cambio password"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

