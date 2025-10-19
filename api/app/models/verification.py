"""
Modelli per il sistema di verifica KYC/KYB
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class VerificationStatus(str, enum.Enum):
    """Stato della verifica"""
    PENDING = "pending"  # In attesa di revisione
    APPROVED = "approved"  # Approvato
    REJECTED = "rejected"  # Rifiutato
    EXPIRED = "expired"  # Scaduto


class VerificationType(str, enum.Enum):
    """Tipo di verifica"""
    KYC = "kyc"  # Know Your Customer (individui)
    KYB = "kyb"  # Know Your Business (aziende)


class Verification(Base):
    """Modello per la verifica KYC/KYB"""
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    verification_type = Column(String, nullable=False)  # KYC o KYB
    status = Column(String, default=VerificationStatus.PENDING, nullable=False)
    
    # Dati personali/aziendali
    full_name = Column(String, nullable=True)  # Per KYC
    date_of_birth = Column(DateTime, nullable=True)  # Per KYC
    company_name = Column(String, nullable=True)  # Per KYB
    vat_number = Column(String, nullable=True)  # Per KYB
    registration_number = Column(String, nullable=True)  # Per KYB
    
    # Documenti
    documents = Column(JSON, nullable=True)  # Lista di documenti caricati
    # Esempio: [{"type": "passport", "url": "/uploads/...", "uploaded_at": "2025-01-15"}]
    
    # Risultati della verifica
    verification_provider = Column(String, nullable=True)  # Es. "onfido", "veriff"
    provider_reference_id = Column(String, nullable=True)  # ID della verifica presso il provider
    verification_result = Column(JSON, nullable=True)  # Risultato dettagliato dal provider
    
    # Approvazione
    approved_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # Data di scadenza della verifica
    
    # Relazioni
    user = relationship("User", foreign_keys=[user_id], backref="verifications")
    approved_by_admin = relationship("User", foreign_keys=[approved_by_admin_id])


class VerificationDocument(Base):
    """Modello per i documenti di verifica"""
    __tablename__ = "verification_documents"

    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(Integer, ForeignKey("verifications.id"), nullable=False, index=True)
    document_type = Column(String, nullable=False)  # Es. "passport", "id_card", "company_registration"
    file_url = Column(String, nullable=False)
    file_hash = Column(String, nullable=True)  # Hash del file per integrità
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relazioni
    verification = relationship("Verification", backref="document_list")


class VerificationAuditLog(Base):
    """Log di audit per le verifiche"""
    __tablename__ = "verification_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(Integer, ForeignKey("verifications.id"), nullable=False, index=True)
    action = Column(String, nullable=False)  # Es. "submitted", "approved", "rejected", "expired"
    performed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relazioni
    verification = relationship("Verification", backref="audit_logs")
    performed_by = relationship("User")

