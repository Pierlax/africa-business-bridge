from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os

from ..core.database import get_db
from ..core.dependencies import get_current_user, require_roles
from ..models.user import User, UserRole
from ..models.training import (
    TrainingEvent, EventRegistration, 
    Course, Lesson, CourseEnrollment
)
from ..schemas.training import (
    TrainingEventCreate, TrainingEventUpdate, TrainingEventResponse, TrainingEventListResponse,
    EventRegistrationCreate, EventRegistrationResponse, EventRegistrationUpdate,
    CourseCreate, CourseUpdate, CourseResponse, CourseListResponse,
    LessonCreate, LessonUpdate, LessonResponse,
    CourseEnrollmentCreate, CourseEnrollmentResponse, CourseEnrollmentUpdate,
    CertificateRequest
)
from ..services.certificate_service import CertificateService

router = APIRouter(prefix="/training", tags=["Formazione"])


# Training Events
@router.get("/events", response_model=TrainingEventListResponse)
def list_events(
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    upcoming: bool = Query(default=False, description="Solo eventi futuri"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista gli eventi formativi con filtri opzionali.
    """
    query = db.query(TrainingEvent)
    
    if event_type:
        query = query.filter(TrainingEvent.event_type == event_type)
    if status:
        query = query.filter(TrainingEvent.status == status)
    if upcoming:
        query = query.filter(TrainingEvent.scheduled_at >= datetime.utcnow())
    
    total = query.count()
    
    # Paginazione
    offset = (page - 1) * page_size
    events = query.order_by(TrainingEvent.scheduled_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": events
    }


@router.get("/events/{event_id}", response_model=TrainingEventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """
    Ottiene un evento specifico.
    """
    event = db.query(TrainingEvent).filter(TrainingEvent.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento non trovato"
        )
    
    return event


@router.post("/events", response_model=TrainingEventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: TrainingEventCreate,
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Crea un nuovo evento formativo (solo admin).
    """
    event = TrainingEvent(**event_data.model_dump())
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return event


@router.put("/events/{event_id}", response_model=TrainingEventResponse)
def update_event(
    event_id: int,
    event_data: TrainingEventUpdate,
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Aggiorna un evento esistente (solo admin).
    """
    event = db.query(TrainingEvent).filter(TrainingEvent.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento non trovato"
        )
    
    for field, value in event_data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    return event


# Event Registrations
@router.post("/events/{event_id}/register", response_model=EventRegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_for_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Registra l'utente corrente a un evento.
    """
    event = db.query(TrainingEvent).filter(TrainingEvent.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento non trovato"
        )
    
    # Verifica se già registrato
    existing = db.query(EventRegistration).filter(
        EventRegistration.event_id == event_id,
        EventRegistration.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Già registrato a questo evento"
        )
    
    # Verifica posti disponibili
    if event.max_participants:
        current_registrations = db.query(EventRegistration).filter(
            EventRegistration.event_id == event_id,
            EventRegistration.status == "registered"
        ).count()
        
        if current_registrations >= event.max_participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evento al completo"
            )
    
    registration = EventRegistration(
        event_id=event_id,
        user_id=current_user.id,
        status="registered"
    )
    
    db.add(registration)
    
    # Aggiorna contatore
    event.registrations_count += 1
    
    db.commit()
    db.refresh(registration)
    
    return registration


@router.get("/events/{event_id}/my-registration", response_model=EventRegistrationResponse)
def get_my_event_registration(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ottiene la registrazione dell'utente corrente per un evento.
    """
    registration = db.query(EventRegistration).filter(
        EventRegistration.event_id == event_id,
        EventRegistration.user_id == current_user.id
    ).first()
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registrazione non trovata"
        )
    
    return registration


@router.put("/registrations/{registration_id}", response_model=EventRegistrationResponse)
def update_registration(
    registration_id: int,
    registration_data: EventRegistrationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aggiorna una registrazione (feedback, ecc.).
    """
    registration = db.query(EventRegistration).filter(
        EventRegistration.id == registration_id,
        EventRegistration.user_id == current_user.id
    ).first()
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registrazione non trovata"
        )
    
    for field, value in registration_data.model_dump(exclude_unset=True).items():
        setattr(registration, field, value)
    
    db.commit()
    db.refresh(registration)
    
    return registration


# Courses
@router.get("/courses", response_model=CourseListResponse)
def list_courses(
    level: Optional[str] = None,
    published_only: bool = True,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista i corsi disponibili.
    """
    query = db.query(Course)
    
    if level:
        query = query.filter(Course.level == level)
    if published_only:
        query = query.filter(Course.is_published == True)
    
    total = query.count()
    
    # Paginazione
    offset = (page - 1) * page_size
    courses = query.offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": courses
    }


@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """
    Ottiene un corso specifico.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corso non trovato"
        )
    
    return course


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Crea un nuovo corso (solo admin).
    """
    course = Course(**course_data.model_dump())
    
    db.add(course)
    db.commit()
    db.refresh(course)
    
    return course


# Lessons
@router.get("/courses/{course_id}/lessons", response_model=List[LessonResponse])
def list_course_lessons(
    course_id: int,
    db: Session = Depends(get_db)
):
    """
    Lista le lezioni di un corso.
    """
    lessons = db.query(Lesson).filter(
        Lesson.course_id == course_id
    ).order_by(Lesson.order_index).all()
    
    return lessons


@router.post("/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(
    lesson_data: LessonCreate,
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Crea una nuova lezione (solo admin).
    """
    lesson = Lesson(**lesson_data.model_dump())
    
    db.add(lesson)
    
    # Aggiorna contatore lezioni del corso
    course = db.query(Course).filter(Course.id == lesson.course_id).first()
    if course:
        course.lessons_count += 1
    
    db.commit()
    db.refresh(lesson)
    
    return lesson


# Course Enrollments
@router.post("/courses/{course_id}/enroll", response_model=CourseEnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_in_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Iscrive l'utente corrente a un corso.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corso non trovato"
        )
    
    # Verifica se già iscritto
    existing = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Già iscritto a questo corso"
        )
    
    enrollment = CourseEnrollment(
        course_id=course_id,
        user_id=current_user.id,
        progress_percentage=0
    )
    
    db.add(enrollment)
    
    # Aggiorna contatore
    course.enrollments_count += 1
    
    db.commit()
    db.refresh(enrollment)
    
    return enrollment


@router.get("/courses/{course_id}/my-enrollment", response_model=CourseEnrollmentResponse)
def get_my_course_enrollment(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ottiene l'iscrizione dell'utente corrente a un corso.
    """
    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.user_id == current_user.id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Iscrizione non trovata"
        )
    
    return enrollment


# Certificates
@router.post("/registrations/{registration_id}/certificate")
def generate_event_certificate(
    registration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Genera un certificato per un evento completato.
    """
    registration = db.query(EventRegistration).filter(
        EventRegistration.id == registration_id,
        EventRegistration.user_id == current_user.id
    ).first()
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registrazione non trovata"
        )
    
    if registration.status != "attended":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Devi aver partecipato all'evento per ottenere il certificato"
        )
    
    event = db.query(TrainingEvent).filter(TrainingEvent.id == registration.event_id).first()
    
    if not event.issues_certificate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Questo evento non rilascia certificati"
        )
    
    # Genera certificato
    cert_service = CertificateService()
    certificate_id = f"event_{registration.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    cert_path = cert_service.generate_event_certificate(
        participant_name=current_user.full_name,
        event_title=event.title,
        event_date=event.scheduled_at or datetime.now(),
        certificate_id=certificate_id
    )
    
    # Salva URL nel database
    registration.certificate_issued = True
    registration.certificate_url = cert_service.get_certificate_url(cert_path)
    
    db.commit()
    
    return {
        "message": "Certificato generato con successo",
        "certificate_url": registration.certificate_url
    }


@router.get("/certificates/{filename}")
def download_certificate(filename: str):
    """
    Scarica un certificato PDF.
    """
    cert_path = f"./certificates/{filename}"
    
    if not os.path.exists(cert_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificato non trovato"
        )
    
    return FileResponse(
        cert_path,
        media_type="application/pdf",
        filename=filename
    )

