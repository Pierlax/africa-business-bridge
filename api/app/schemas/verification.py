"""
Schemi Pydantic per il modulo di verifica KYC/KYB
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr


class VerificationDocumentSchema(BaseModel):
    """Schema per i documenti di verifica"""
    document_type: str
    file_url: str
    uploaded_at: datetime


class VerificationCreateSchema(BaseModel):
    """Schema per la creazione di una verifica"""
    verification_type: str  # "kyc" o "kyb"
    full_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    company_name: Optional[str] = None
    vat_number: Optional[str] = None
    registration_number: Optional[str] = None


class VerificationUpdateSchema(BaseModel):
    """Schema per l'aggiornamento di una verifica"""
    status: Optional[str] = None
    approval_notes: Optional[str] = None


class VerificationResponseSchema(BaseModel):
    """Schema per la risposta di una verifica"""
    id: int
    user_id: int
    verification_type: str
    status: str
    full_name: Optional[str]
    company_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True

