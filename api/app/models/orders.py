"""
Modelli per il sistema di gestione ordini (OMS)
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Enum, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class OrderStatus(str, enum.Enum):
    """Stato dell'ordine"""
    DRAFT = "draft"  # Bozza
    SUBMITTED = "submitted"  # Inviato
    ACCEPTED = "accepted"  # Accettato dal partner
    IN_PROGRESS = "in_progress"  # In corso
    COMPLETED = "completed"  # Completato
    CANCELLED = "cancelled"  # Cancellato
    DISPUTED = "disputed"  # In disputa


class Order(Base):
    """Modello per gli ordini B2B"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, nullable=False, index=True)  # Es. "ORD-2025-001"
    
    # Parti coinvolte
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # PMI
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Partner Locale
    
    # Informazioni ordine
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default=OrderStatus.DRAFT, nullable=False)
    
    # Importi
    total_amount = Column(Float, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    
    # Blockchain
    smart_contract_address = Column(String, nullable=True)  # Indirizzo dello smart contract associato
    blockchain_transaction_hash = Column(String, nullable=True)  # Hash della transazione blockchain
    
    # Scadenze
    delivery_date = Column(DateTime, nullable=True)
    payment_terms = Column(String, nullable=True)  # Es. "NET30", "COD"
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relazioni
    buyer = relationship("User", foreign_keys=[buyer_id], backref="orders_as_buyer")
    seller = relationship("User", foreign_keys=[seller_id], backref="orders_as_seller")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    milestones = relationship("OrderMilestone", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("OrderPayment", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Modello per le voci d'ordine"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)  # Riferimento al prodotto se disponibile
    
    # Descrizione dell'articolo
    description = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # Es. "kg", "pcs", "m3"
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Specifiche
    specifications = Column(JSON, nullable=True)  # Dettagli tecnici
    
    # Relazioni
    order = relationship("Order", back_populates="items")
    product = relationship("Product")


class OrderMilestone(Base):
    """Modello per le milestone dell'ordine (collegate ai contratti blockchain)"""
    __tablename__ = "order_milestones"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    milestone_number = Column(Integer, nullable=False)  # 1, 2, 3, ecc.
    
    # Descrizione
    description = Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending, in_progress, completed, released
    
    # Importo
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    
    # Scadenza
    due_date = Column(DateTime, nullable=True)
    
    # Blockchain
    blockchain_milestone_id = Column(Integer, nullable=True)  # ID della milestone nello smart contract
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    payment_released_at = Column(DateTime, nullable=True)
    
    # Relazioni
    order = relationship("Order", back_populates="milestones")


class OrderPayment(Base):
    """Modello per i pagamenti dell'ordine"""
    __tablename__ = "order_payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    milestone_id = Column(Integer, ForeignKey("order_milestones.id"), nullable=True)
    
    # Importo
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    
    # Stato pagamento
    status = Column(String, default="pending", nullable=False)  # pending, released, completed, failed
    
    # Blockchain
    blockchain_transaction_hash = Column(String, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    released_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relazioni
    order = relationship("Order", back_populates="payments")
    milestone = relationship("OrderMilestone")


class OrderDispute(Base):
    """Modello per le dispute degli ordini"""
    __tablename__ = "order_disputes"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    raised_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Descrizione della disputa
    reason = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Stato
    status = Column(String, default="open", nullable=False)  # open, in_review, resolved, closed
    
    # Risoluzione
    resolution = Column(Text, nullable=True)
    resolved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relazioni
    order = relationship("Order")
    raised_by = relationship("User", foreign_keys=[raised_by_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])

