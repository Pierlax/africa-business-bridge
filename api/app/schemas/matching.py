from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from ..models.business import MatchStatus


# BusinessMatch Schemas
class MatchBreakdown(BaseModel):
    """Breakdown dettagliato dei punteggi di matching"""
    sector_score: float
    country_score: float
    service_score: float
    size_score: float
    keyword_score: float
    total_score: float


class PartnerSummary(BaseModel):
    """Riepilogo informazioni partner per il matching"""
    id: int
    company_name: str
    country: str
    city: Optional[str] = None
    partner_type: Optional[str] = None
    services_offered: Optional[str] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class MatchSuggestion(BaseModel):
    """Suggerimento di match con spiegazione"""
    partner_id: int
    partner_name: str
    match_score: float
    explanation: str
    breakdown: MatchBreakdown
    partner_data: PartnerSummary


class MatchSuggestionsResponse(BaseModel):
    """Risposta con lista di suggerimenti di match"""
    total: int
    matches: List[MatchSuggestion]


class BusinessMatchResponse(BaseModel):
    """Risposta con dettagli di un match"""
    id: int
    pmi_id: int
    partner_id: int
    match_score: Optional[float] = None
    match_reason: Optional[str] = None
    status: MatchStatus
    pmi_notes: Optional[str] = None
    partner_notes: Optional[str] = None
    pmi_rating: Optional[int] = None
    partner_rating: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MatchAcceptRequest(BaseModel):
    """Richiesta per accettare un match"""
    notes: Optional[str] = None


class MatchUpdateRequest(BaseModel):
    """Richiesta per aggiornare un match"""
    status: Optional[MatchStatus] = None
    notes: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


# Meeting Schemas
class MeetingBase(BaseModel):
    """Schema base per Meeting"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int = Field(default=60, ge=15, le=480)
    meeting_platform: Optional[str] = Field(None, max_length=50)


class MeetingCreate(MeetingBase):
    """Schema per la creazione di un Meeting"""
    partner_id: int
    match_id: Optional[int] = None


class MeetingUpdate(BaseModel):
    """Schema per l'aggiornamento di un Meeting"""
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    action_items: Optional[str] = None


class MeetingResponse(MeetingBase):
    """Schema per la risposta con Meeting"""
    id: int
    match_id: Optional[int] = None
    pmi_id: int
    partner_id: int
    meeting_url: Optional[str] = None
    status: str
    notes: Optional[str] = None
    action_items: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MeetingListResponse(BaseModel):
    """Schema per la lista paginata di meeting"""
    total: int
    items: List[MeetingResponse]


# Message Schemas
class MessageBase(BaseModel):
    """Schema base per Message"""
    subject: Optional[str] = Field(None, max_length=255)
    body: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
    """Schema per la creazione di un Message"""
    recipient_id: int
    match_id: Optional[int] = None
    meeting_id: Optional[int] = None


class MessageResponse(MessageBase):
    """Schema per la risposta con Message"""
    id: int
    sender_id: int
    recipient_id: int
    is_read: bool
    read_at: Optional[datetime] = None
    match_id: Optional[int] = None
    meeting_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Schema per la lista paginata di messaggi"""
    total: int
    unread_count: int
    items: List[MessageResponse]

