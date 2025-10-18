from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class MatchStatus(str, enum.Enum):
    """Stati del matching"""
    SUGGESTED = "suggested"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    MEETING_SCHEDULED = "meeting_scheduled"
    COMPLETED = "completed"


class BusinessMatch(Base):
    """Match tra PMI e Partner Locali"""
    __tablename__ = "business_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    pmi_id = Column(Integer, ForeignKey("pmi_profiles.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("partner_profiles.id"), nullable=False)
    
    # Informazioni match
    match_score = Column(Float)  # Score di compatibilità (0-100)
    match_reason = Column(Text)  # Spiegazione del match
    status = Column(Enum(MatchStatus), default=MatchStatus.SUGGESTED)
    
    # Note e feedback
    pmi_notes = Column(Text)
    partner_notes = Column(Text)
    pmi_rating = Column(Integer)  # 1-5 stelle
    partner_rating = Column(Integer)  # 1-5 stelle
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Meeting(Base):
    """Incontri B2B tra PMI e Partner"""
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("business_matches.id"))
    pmi_id = Column(Integer, ForeignKey("pmi_profiles.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("partner_profiles.id"), nullable=False)
    
    # Informazioni meeting
    title = Column(String(255), nullable=False)
    description = Column(Text)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=60)
    
    # Link videocall
    meeting_url = Column(String(500))  # URL Zoom/Google Meet
    meeting_platform = Column(String(50))  # zoom, google_meet, teams
    
    # Status
    status = Column(String(50), default="scheduled")  # scheduled, completed, cancelled
    
    # Note post-meeting
    notes = Column(Text)
    action_items = Column(Text)  # JSON array di azioni da intraprendere
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Message(Base):
    """Messaggi tra utenti della piattaforma"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Contenuto
    subject = Column(String(255))
    body = Column(Text, nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    
    # Relazioni (opzionale)
    match_id = Column(Integer, ForeignKey("business_matches.id"))
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MarketReport(Base):
    """Report e analisi di mercato"""
    __tablename__ = "market_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informazioni report
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text)  # Contenuto completo del report
    summary = Column(Text)  # Sommario esecutivo
    
    # Categorizzazione
    country = Column(String(100))  # Kenya, Tanzania, Etiopia
    sector = Column(String(255))
    report_type = Column(String(100))  # market_analysis, sector_study, opportunity, regulation
    
    # File allegati
    file_url = Column(String(500))
    cover_image_url = Column(String(500))
    
    # Metadati
    author = Column(String(255))
    source = Column(String(255))  # ICE, SACE, InfoMercatiEsteri, etc.
    publication_date = Column(DateTime(timezone=True))
    
    # SEO e ricerca
    keywords = Column(Text)  # JSON array di keywords
    is_featured = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)  # Richiede abbonamento premium
    
    # Statistiche
    views_count = Column(Integer, default=0)
    downloads_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NewsItem(Base):
    """Notizie e aggiornamenti dai mercati target"""
    __tablename__ = "news_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Contenuto
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    content = Column(Text)
    url = Column(String(500))  # URL fonte originale
    image_url = Column(String(500))
    
    # Categorizzazione
    country = Column(String(100))
    category = Column(String(100))  # economy, business, regulation, tender, etc.
    sector = Column(String(255))
    
    # Metadati
    source = Column(String(255))  # Nome della fonte
    author = Column(String(255))
    published_at = Column(DateTime(timezone=True))
    
    # SEO e ricerca
    keywords = Column(Text)  # JSON array di keywords
    
    # Statistiche
    views_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Alert(Base):
    """Alert personalizzati per gli utenti"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Configurazione alert
    name = Column(String(255), nullable=False)
    keywords = Column(Text, nullable=False)  # JSON array di keywords
    countries = Column(Text)  # JSON array di paesi
    sectors = Column(Text)  # JSON array di settori
    alert_types = Column(Text)  # JSON array: news, reports, tenders
    
    # Notifiche
    email_notification = Column(Boolean, default=True)
    frequency = Column(String(50), default="immediate")  # immediate, daily, weekly
    
    # Status
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

