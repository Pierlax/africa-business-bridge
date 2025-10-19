"""
Modelli per i moduli di logistica e ispezione
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Enum, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ShipmentStatus(str, enum.Enum):
    """Stato della spedizione"""
    QUOTE_REQUESTED = "quote_requested"  # Quotazione richiesta
    QUOTE_RECEIVED = "quote_received"  # Quotazione ricevuta
    BOOKED = "booked"  # Prenotata
    PICKED_UP = "picked_up"  # Ritirata
    IN_TRANSIT = "in_transit"  # In transito
    DELIVERED = "delivered"  # Consegnata
    CANCELLED = "cancelled"  # Cancellata


class Shipment(Base):
    """Modello per le spedizioni"""
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    shipment_number = Column(String, unique=True, nullable=False, index=True)  # Es. "SHIP-2025-001"
    
    # Ordine associato
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    # Mittente e destinatario
    shipper_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Indirizzi
    origin_address = Column(String, nullable=False)
    origin_country = Column(String, nullable=False)
    destination_address = Column(String, nullable=False)
    destination_country = Column(String, nullable=False)
    
    # Dettagli della merce
    description = Column(Text, nullable=False)
    weight_kg = Column(Float, nullable=True)
    volume_m3 = Column(Float, nullable=True)
    value = Column(Float, nullable=True)
    currency = Column(String, default="USD", nullable=False)
    
    # Status
    status = Column(String, default=ShipmentStatus.QUOTE_REQUESTED, nullable=False)
    
    # Provider logistico
    logistics_provider = Column(String, nullable=True)  # Es. "DHL", "FedEx", "Local Provider"
    tracking_number = Column(String, nullable=True)
    
    # Costi
    shipping_cost = Column(Float, nullable=True)
    insurance_cost = Column(Float, nullable=True)
    carbon_offset_cost = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=True)
    
    # Carbon offsetting
    estimated_carbon_emissions_kg = Column(Float, nullable=True)
    carbon_offset_provider = Column(String, nullable=True)  # Es. "Gold Standard", "Verra"
    carbon_offset_certificate_url = Column(String, nullable=True)
    
    # Date
    pickup_date = Column(DateTime, nullable=True)
    expected_delivery_date = Column(DateTime, nullable=True)
    actual_delivery_date = Column(DateTime, nullable=True)
    
    # Blockchain
    blockchain_transaction_hash = Column(String, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relazioni
    order = relationship("Order")
    shipper = relationship("User", foreign_keys=[shipper_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    tracking_events = relationship("ShipmentTrackingEvent", back_populates="shipment", cascade="all, delete-orphan")
    inspections = relationship("Inspection", back_populates="shipment")


class ShipmentTrackingEvent(Base):
    """Modello per gli eventi di tracciamento della spedizione"""
    __tablename__ = "shipment_tracking_events"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False, index=True)
    
    # Evento
    event_type = Column(String, nullable=False)  # Es. "pickup", "in_transit", "delivery", "exception"
    description = Column(String, nullable=False)
    location = Column(String, nullable=True)
    
    # Timestamp
    event_timestamp = Column(DateTime, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Blockchain
    blockchain_transaction_hash = Column(String, nullable=True)
    
    # Relazioni
    shipment = relationship("Shipment", back_populates="tracking_events")


class InspectionStatus(str, enum.Enum):
    """Stato dell'ispezione"""
    QUOTE_REQUESTED = "quote_requested"  # Quotazione richiesta
    QUOTE_RECEIVED = "quote_received"  # Quotazione ricevuta
    SCHEDULED = "scheduled"  # Programmata
    IN_PROGRESS = "in_progress"  # In corso
    COMPLETED = "completed"  # Completata
    CANCELLED = "cancelled"  # Cancellata


class Inspection(Base):
    """Modello per le ispezioni"""
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    inspection_number = Column(String, unique=True, nullable=False, index=True)  # Es. "INSP-2025-001"
    
    # Ordine e spedizione associati
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=True)
    
    # Richiedente
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Dettagli dell'ispezione
    inspection_type = Column(String, nullable=False)  # Es. "quality", "quantity", "documentation", "customs"
    description = Column(Text, nullable=False)
    location = Column(String, nullable=False)
    
    # Status
    status = Column(String, default=InspectionStatus.QUOTE_REQUESTED, nullable=False)
    
    # Provider di ispezione
    inspection_provider = Column(String, nullable=True)  # Es. "SGS", "TÜV", "Local Inspector"
    
    # Costi
    inspection_cost = Column(Float, nullable=True)
    currency = Column(String, default="USD", nullable=False)
    
    # Date
    scheduled_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)
    
    # Risultati
    findings = Column(JSON, nullable=True)  # Risultati dettagliati dell'ispezione
    report_url = Column(String, nullable=True)  # URL del report PDF
    
    # Blockchain
    blockchain_transaction_hash = Column(String, nullable=True)
    report_hash = Column(String, nullable=True)  # Hash del report per integrità
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relazioni
    order = relationship("Order")
    shipment = relationship("Shipment", back_populates="inspections")
    requested_by = relationship("User")


class LogisticsQuote(Base):
    """Modello per le quotazioni di logistica"""
    __tablename__ = "logistics_quotes"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False, index=True)
    
    # Provider
    provider_name = Column(String, nullable=False)
    provider_contact = Column(String, nullable=True)
    
    # Dettagli della quotazione
    shipping_cost = Column(Float, nullable=False)
    insurance_cost = Column(Float, nullable=True)
    estimated_delivery_days = Column(Integer, nullable=True)
    
    # Validità
    valid_until = Column(DateTime, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relazioni
    shipment = relationship("Shipment")

