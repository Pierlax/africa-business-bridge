from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class ExpoPage(Base):
    """Pagina vetrina dell'Expo Virtuale per ogni PMI"""
    __tablename__ = "expo_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    pmi_id = Column(Integer, ForeignKey("pmi_profiles.id"), unique=True, nullable=False)
    
    # Contenuti della pagina
    title = Column(String(255))
    subtitle = Column(String(255))
    description = Column(Text)
    logo_url = Column(String(500))
    banner_url = Column(String(500))
    video_url = Column(String(500))  # URL YouTube/Vimeo
    
    # Personalizzazione
    theme_color = Column(String(7), default="#0066CC")  # Colore tema in hex
    custom_css = Column(Text)  # CSS personalizzato
    
    # SEO
    meta_title = Column(String(255))
    meta_description = Column(Text)
    keywords = Column(Text)  # JSON array di keywords
    
    # Statistiche
    views_count = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relazioni
    pmi = relationship("PMIProfile", back_populates="expo_page")
    media_gallery = relationship("MediaItem", back_populates="expo_page", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="expo_page", cascade="all, delete-orphan")


class Product(Base):
    """Prodotti nel catalogo dell'azienda PMI"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    pmi_id = Column(Integer, ForeignKey("pmi_profiles.id"), nullable=False)
    
    # Informazioni prodotto
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    subcategory = Column(String(100))
    
    # Dettagli tecnici
    specifications = Column(Text)  # JSON con specifiche tecniche
    certifications = Column(Text)  # JSON con certificazioni
    
    # Immagini e media
    main_image_url = Column(String(500))
    images_urls = Column(Text)  # JSON array di URL immagini
    
    # Pricing (opzionale)
    price = Column(Float)
    currency = Column(String(3), default="EUR")
    price_notes = Column(Text)
    
    # SEO e ricerca
    keywords = Column(Text)  # JSON array di keywords
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relazioni
    pmi = relationship("PMIProfile", back_populates="products")


class MediaItem(Base):
    """Media gallery per l'Expo Virtuale"""
    __tablename__ = "media_items"
    
    id = Column(Integer, primary_key=True, index=True)
    expo_page_id = Column(Integer, ForeignKey("expo_pages.id"), nullable=False)
    
    # Informazioni media
    title = Column(String(255))
    description = Column(Text)
    media_type = Column(String(50))  # image, video
    url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    
    # Metadati
    file_size = Column(Integer)  # in bytes
    mime_type = Column(String(100))
    order_index = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relazioni
    expo_page = relationship("ExpoPage", back_populates="media_gallery")


class Document(Base):
    """Documenti (brochure, cataloghi PDF) per l'Expo Virtuale"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    expo_page_id = Column(Integer, ForeignKey("expo_pages.id"), nullable=False)
    
    # Informazioni documento
    title = Column(String(255), nullable=False)
    description = Column(Text)
    file_url = Column(String(500), nullable=False)
    file_name = Column(String(255))
    file_size = Column(Integer)  # in bytes
    mime_type = Column(String(100))
    
    # Statistiche
    downloads_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relazioni
    expo_page = relationship("ExpoPage", back_populates="documents")

