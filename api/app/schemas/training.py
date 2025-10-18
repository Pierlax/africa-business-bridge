from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


# TrainingEvent Schemas
class TrainingEventBase(BaseModel):
    """Schema base per TrainingEvent"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_type: str = Field(..., max_length=50)  # webinar, workshop, course
    status: str = Field(default="draft", max_length=20)  # draft, published, live, completed
    cover_image_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15)
    max_participants: Optional[int] = Field(None, ge=1)
    meeting_url: Optional[str] = None
    recording_url: Optional[str] = None
    materials_url: Optional[str] = None
    instructor_name: Optional[str] = Field(None, max_length=255)
    instructor_bio: Optional[str] = None
    issues_certificate: bool = False


class TrainingEventCreate(TrainingEventBase):
    """Schema per la creazione di un TrainingEvent"""
    pass


class TrainingEventUpdate(BaseModel):
    """Schema per l'aggiornamento di un TrainingEvent"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    max_participants: Optional[int] = None
    meeting_url: Optional[str] = None
    recording_url: Optional[str] = None
    materials_url: Optional[str] = None
    issues_certificate: Optional[bool] = None


class TrainingEventResponse(TrainingEventBase):
    """Schema per la risposta con TrainingEvent"""
    id: int
    registrations_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TrainingEventListResponse(BaseModel):
    """Schema per la lista paginata di eventi"""
    total: int
    page: int
    page_size: int
    items: List[TrainingEventResponse]


# EventRegistration Schemas
class EventRegistrationCreate(BaseModel):
    """Schema per la registrazione a un evento"""
    event_id: int
    notes: Optional[str] = None


class EventRegistrationResponse(BaseModel):
    """Schema per la risposta con EventRegistration"""
    id: int
    event_id: int
    user_id: int
    status: str  # registered, attended, cancelled
    attended_at: Optional[datetime] = None
    certificate_issued: bool
    certificate_url: Optional[str] = None
    feedback_rating: Optional[int] = None
    feedback_comment: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class EventRegistrationUpdate(BaseModel):
    """Schema per l'aggiornamento di una registrazione"""
    status: Optional[str] = None
    feedback_rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_comment: Optional[str] = None


# Course Schemas
class CourseBase(BaseModel):
    """Schema base per Course"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    level: str = Field(default="beginner", max_length=20)  # beginner, intermediate, advanced
    duration_hours: Optional[int] = Field(None, ge=1)
    cover_image_url: Optional[str] = None
    instructor_name: Optional[str] = Field(None, max_length=255)
    instructor_bio: Optional[str] = None
    is_published: bool = False
    issues_certificate: bool = True


class CourseCreate(CourseBase):
    """Schema per la creazione di un Course"""
    pass


class CourseUpdate(BaseModel):
    """Schema per l'aggiornamento di un Course"""
    title: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None
    duration_hours: Optional[int] = None
    is_published: Optional[bool] = None


class CourseResponse(CourseBase):
    """Schema per la risposta con Course"""
    id: int
    enrollments_count: int
    lessons_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CourseListResponse(BaseModel):
    """Schema per la lista paginata di corsi"""
    total: int
    page: int
    page_size: int
    items: List[CourseResponse]


# Lesson Schemas
class LessonBase(BaseModel):
    """Schema base per Lesson"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=1)
    order_index: int = Field(default=0)
    is_published: bool = False


class LessonCreate(LessonBase):
    """Schema per la creazione di una Lesson"""
    course_id: int


class LessonUpdate(BaseModel):
    """Schema per l'aggiornamento di una Lesson"""
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    order_index: Optional[int] = None
    is_published: Optional[bool] = None


class LessonResponse(LessonBase):
    """Schema per la risposta con Lesson"""
    id: int
    course_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# CourseEnrollment Schemas
class CourseEnrollmentCreate(BaseModel):
    """Schema per l'iscrizione a un corso"""
    course_id: int


class CourseEnrollmentResponse(BaseModel):
    """Schema per la risposta con CourseEnrollment"""
    id: int
    course_id: int
    user_id: int
    progress_percentage: int
    completed_lessons: Optional[str] = None  # JSON array
    completed_at: Optional[datetime] = None
    certificate_issued: bool
    certificate_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class CourseEnrollmentUpdate(BaseModel):
    """Schema per l'aggiornamento di un'iscrizione"""
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    completed_lessons: Optional[str] = None


# Certificate Request
class CertificateRequest(BaseModel):
    """Schema per la richiesta di generazione certificato"""
    participant_name: str
    event_or_course_title: str
    completion_date: datetime
    certificate_type: str  # event, course

