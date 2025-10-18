from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class EventType(str, enum.Enum):
    """Tipi di eventi formativi"""
    WEBINAR = "webinar"
    COURSE = "course"
    WORKSHOP = "workshop"
    CONFERENCE = "conference"


class EventStatus(str, enum.Enum):
    """Stati degli eventi"""
    DRAFT = "draft"
    PUBLISHED = "published"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TrainingEvent(Base):
    """Eventi formativi (webinar, corsi, workshop)"""
    __tablename__ = "training_events"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informazioni evento
    title = Column(String(255), nullable=False)
    description = Column(Text)
    event_type = Column(Enum(EventType), nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.DRAFT)
    
    # Contenuto
    cover_image_url = Column(String(500))
    video_url = Column(String(500))  # Per eventi on-demand
    live_url = Column(String(500))  # Link Zoom/altro per eventi live
    materials_urls = Column(Text)  # JSON array di URL materiali didattici
    
    # Categorizzazione
    category = Column(String(100))
    topics = Column(Text)  # JSON array di argomenti
    target_audience = Column(String(255))  # PMI, Partner, Tutti
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    timezone = Column(String(50), default="Europe/Rome")
    
    # Docenti/Relatori
    instructors = Column(Text)  # JSON array con info docenti
    
    # Capacità e registrazioni
    max_participants = Column(Integer)
    registration_deadline = Column(DateTime(timezone=True))
    requires_approval = Column(Boolean, default=False)
    
    # Certificazione
    issues_certificate = Column(Boolean, default=True)
    certificate_template = Column(String(255))
    
    # Statistiche
    views_count = Column(Integer, default=0)
    registrations_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relazioni
    registrations = relationship("EventRegistration", back_populates="event", cascade="all, delete-orphan")


class EventRegistration(Base):
    """Registrazioni agli eventi formativi"""
    __tablename__ = "event_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("training_events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status registrazione
    status = Column(String(50), default="registered")  # registered, approved, attended, cancelled
    
    # Partecipazione
    attended = Column(Boolean, default=False)
    attendance_duration_minutes = Column(Integer)  # Durata effettiva partecipazione
    
    # Certificato
    certificate_issued = Column(Boolean, default=False)
    certificate_url = Column(String(500))
    certificate_issued_at = Column(DateTime(timezone=True))
    
    # Feedback
    rating = Column(Integer)  # 1-5 stelle
    feedback = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relazioni
    event = relationship("TrainingEvent", back_populates="registrations")


class Course(Base):
    """Corsi strutturati con più lezioni"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informazioni corso
    title = Column(String(255), nullable=False)
    description = Column(Text)
    cover_image_url = Column(String(500))
    
    # Categorizzazione
    category = Column(String(100))
    level = Column(String(50))  # beginner, intermediate, advanced
    topics = Column(Text)  # JSON array di argomenti
    
    # Durata e struttura
    total_duration_minutes = Column(Integer)
    lessons_count = Column(Integer)
    
    # Docenti
    instructors = Column(Text)  # JSON array con info docenti
    
    # Accesso
    is_free = Column(Boolean, default=True)
    price = Column(Integer)
    is_published = Column(Boolean, default=False)
    
    # Certificazione
    issues_certificate = Column(Boolean, default=True)
    
    # Statistiche
    enrollments_count = Column(Integer, default=0)
    average_rating = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relazioni
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")


class Lesson(Base):
    """Lezioni all'interno di un corso"""
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    # Informazioni lezione
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer, nullable=False)
    
    # Contenuto
    video_url = Column(String(500))
    duration_minutes = Column(Integer)
    materials_urls = Column(Text)  # JSON array di URL materiali
    
    # Status
    is_published = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relazioni
    course = relationship("Course", back_populates="lessons")


class CourseEnrollment(Base):
    """Iscrizioni ai corsi"""
    __tablename__ = "course_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Progresso
    progress_percentage = Column(Integer, default=0)
    completed_lessons = Column(Text)  # JSON array di lesson_id completate
    last_accessed_lesson_id = Column(Integer)
    
    # Completamento
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    
    # Certificato
    certificate_issued = Column(Boolean, default=False)
    certificate_url = Column(String(500))
    
    # Feedback
    rating = Column(Integer)  # 1-5 stelle
    review = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relazioni
    course = relationship("Course", back_populates="enrollments")

