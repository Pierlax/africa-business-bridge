from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from ..core.database import Base


class UserRole(str, enum.Enum):
    """Ruoli utente nella piattaforma"""
    PMI = "pmi"  # Azienda PMI
    PARTNER = "partner"  # Partner Locale
    ADMIN = "admin"  # Amministratore IBP


class User(Base):
    """Modello base per tutti gli utenti della piattaforma"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relazioni
    pmi_profile = relationship("PMIProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    partner_profile = relationship("PartnerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    admin_profile = relationship("AdminProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class PMIProfile(Base):
    """Profilo specifico per le aziende PMI"""
    __tablename__ = "pmi_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Informazioni aziendali
    company_name = Column(String(255), nullable=False)
    vat_number = Column(String(50), unique=True)
    company_size = Column(String(50))  # micro, piccola, media
    sector = Column(String(255))  # Settore merceologico
    description = Column(Text)
    website = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100), default="Italia")
    
    # Obiettivi di business
    business_objectives = Column(Text)  # JSON string con obiettivi
    target_markets = Column(Text)  # JSON string con mercati target (Kenya, Tanzania, Etiopia)
    production_capacity = Column(String(100))
    
    # Relazioni
    user = relationship("User", back_populates="pmi_profile")
    products = relationship("Product", back_populates="pmi", cascade="all, delete-orphan")
    expo_page = relationship("ExpoPage", back_populates="pmi", uselist=False, cascade="all, delete-orphan")


class PartnerProfile(Base):
    """Profilo specifico per i Partner Locali"""
    __tablename__ = "partner_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Informazioni partner
    company_name = Column(String(255), nullable=False)
    partner_type = Column(String(100))  # distributore, legale, logistica, consulente, etc.
    country = Column(String(100))  # Kenya, Tanzania, Etiopia
    city = Column(String(100))
    description = Column(Text)
    services_offered = Column(Text)  # JSON string con servizi offerti
    sectors_expertise = Column(Text)  # JSON string con settori di competenza
    website = Column(String(255))
    phone = Column(String(50))
    
    # Visibilità e disponibilità
    is_public = Column(Boolean, default=True)
    availability_status = Column(String(50), default="available")  # available, busy, unavailable
    
    # Relazioni
    user = relationship("User", back_populates="partner_profile")


class AdminProfile(Base):
    """Profilo specifico per gli Amministratori IBP"""
    __tablename__ = "admin_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Informazioni admin
    department = Column(String(100))
    permissions = Column(Text)  # JSON string con permessi specifici
    
    # Relazioni
    user = relationship("User", back_populates="admin_profile")

