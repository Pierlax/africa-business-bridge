"""
API routes per il modulo di verifica KYC/KYB
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.verification import Verification, VerificationStatus
from app.schemas.verification import (
    VerificationCreateSchema,
    VerificationUpdateSchema,
    VerificationResponseSchema,
)

router = APIRouter(prefix="/api/v1/verification", tags=["verification"])


@router.post("/submit", response_model=VerificationResponseSchema)
def submit_verification(
    verification_data: VerificationCreateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Sottometti una richiesta di verifica KYC/KYB.
    """
    # Controlla se esiste già una verifica attiva
    existing_verification = db.query(Verification).filter(
        Verification.user_id == current_user.id,
        Verification.verification_type == verification_data.verification_type,
        Verification.status.in_([VerificationStatus.PENDING, VerificationStatus.APPROVED])
    ).first()
    
    if existing_verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Una verifica di questo tipo è già in corso o approvata."
        )
    
    # Crea una nuova verifica
    verification = Verification(
        user_id=current_user.id,
        verification_type=verification_data.verification_type,
        full_name=verification_data.full_name,
        date_of_birth=verification_data.date_of_birth,
        company_name=verification_data.company_name,
        vat_number=verification_data.vat_number,
        registration_number=verification_data.registration_number,
        status=VerificationStatus.PENDING,
    )
    
    db.add(verification)
    db.commit()
    db.refresh(verification)
    
    return verification


@router.get("/status", response_model=VerificationResponseSchema)
def get_verification_status(
    verification_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Ottieni lo stato della verifica dell'utente corrente.
    """
    verification = db.query(Verification).filter(
        Verification.user_id == current_user.id,
        Verification.verification_type == verification_type,
    ).order_by(Verification.created_at.desc()).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nessuna verifica trovata."
        )
    
    return verification


@router.get("/admin/pending", response_model=list[VerificationResponseSchema])
def get_pending_verifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Ottieni tutte le verifiche in sospeso (solo admin).
    """
    # Controlla se l'utente è admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso negato."
        )
    
    verifications = db.query(Verification).filter(
        Verification.status == VerificationStatus.PENDING
    ).all()
    
    return verifications


@router.put("/admin/{verification_id}/approve")
def approve_verification(
    verification_id: int,
    update_data: VerificationUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Approva una verifica (solo admin).
    """
    # Controlla se l'utente è admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso negato."
        )
    
    verification = db.query(Verification).filter(
        Verification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verifica non trovata."
        )
    
    verification.status = VerificationStatus.APPROVED
    verification.approved_by_admin_id = current_user.id
    verification.approval_notes = update_data.approval_notes
    
    db.commit()
    db.refresh(verification)
    
    return {"message": "Verifica approvata con successo."}


@router.put("/admin/{verification_id}/reject")
def reject_verification(
    verification_id: int,
    update_data: VerificationUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Rifiuta una verifica (solo admin).
    """
    # Controlla se l'utente è admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso negato."
        )
    
    verification = db.query(Verification).filter(
        Verification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verifica non trovata."
        )
    
    verification.status = VerificationStatus.REJECTED
    verification.approval_notes = update_data.approval_notes
    
    db.commit()
    db.refresh(verification)
    
    return {"message": "Verifica rifiutata con successo."}

