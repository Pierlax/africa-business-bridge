from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.dependencies import get_current_user, require_pmi, require_partner, require_roles
from ..models.user import User, UserRole, PMIProfile, PartnerProfile
from ..models.business import BusinessMatch, Meeting, Message, MatchStatus
from ..schemas.matching import (
    MatchSuggestionsResponse,
    MatchSuggestion,
    MatchBreakdown,
    PartnerSummary,
    BusinessMatchResponse,
    MatchAcceptRequest,
    MatchUpdateRequest,
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingListResponse,
    MessageCreate,
    MessageResponse,
    MessageListResponse
)
from ..services.matching_service import MatchingService

router = APIRouter(prefix="/matching", tags=["Business Matching"])


# Match Suggestions
@router.get("/suggestions", response_model=MatchSuggestionsResponse)
def get_match_suggestions(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(require_pmi),
    db: Session = Depends(get_db)
):
    """
    Ottiene suggerimenti di match per la PMI corrente usando l'algoritmo IA.
    """
    # Ottieni profilo PMI
    pmi_profile = db.query(PMIProfile).filter(PMIProfile.user_id == current_user.id).first()
    
    if not pmi_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profilo PMI non trovato"
        )
    
    # Usa il servizio di matching
    matching_service = MatchingService(db)
    matches = matching_service.find_matches_for_pmi(pmi_profile.id, limit=limit)
    
    # Converti in formato risposta
    suggestions = []
    for match in matches:
        # Ottieni profilo partner completo
        partner_profile = db.query(PartnerProfile).filter(
            PartnerProfile.id == match['partner_id']
        ).first()
        
        if partner_profile:
            suggestions.append(MatchSuggestion(
                partner_id=match['partner_id'],
                partner_name=match['partner_name'],
                match_score=match['match_score'],
                explanation=match['explanation'],
                breakdown=MatchBreakdown(**match['breakdown']),
                partner_data=PartnerSummary(
                    id=partner_profile.id,
                    company_name=partner_profile.company_name,
                    country=partner_profile.country,
                    city=partner_profile.city,
                    partner_type=partner_profile.partner_type,
                    services_offered=partner_profile.services_offered,
                    description=partner_profile.description
                )
            ))
    
    return {
        "total": len(suggestions),
        "matches": suggestions
    }


# Accept Match
@router.post("/accept/{partner_id}", response_model=BusinessMatchResponse)
def accept_match(
    partner_id: int,
    request: MatchAcceptRequest,
    current_user: User = Depends(require_pmi),
    db: Session = Depends(get_db)
):
    """
    Accetta un match suggerito con un partner.
    """
    # Ottieni profilo PMI
    pmi_profile = db.query(PMIProfile).filter(PMIProfile.user_id == current_user.id).first()
    
    if not pmi_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profilo PMI non trovato"
        )
    
    # Verifica che il partner esista
    partner_profile = db.query(PartnerProfile).filter(PartnerProfile.id == partner_id).first()
    
    if not partner_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner non trovato"
        )
    
    # Verifica se esiste già un match
    existing_match = db.query(BusinessMatch).filter(
        BusinessMatch.pmi_id == pmi_profile.id,
        BusinessMatch.partner_id == partner_id
    ).first()
    
    if existing_match:
        # Aggiorna match esistente
        matching_service = MatchingService(db)
        match = matching_service.accept_match(existing_match.id, 'pmi', request.notes)
    else:
        # Crea nuovo match accettato
        match = BusinessMatch(
            pmi_id=pmi_profile.id,
            partner_id=partner_id,
            status=MatchStatus.ACCEPTED,
            pmi_notes=request.notes
        )
        db.add(match)
        db.commit()
        db.refresh(match)
    
    return match


# Get My Matches
@router.get("/my-matches", response_model=List[BusinessMatchResponse])
def get_my_matches(
    status: Optional[MatchStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ottiene tutti i match dell'utente corrente.
    """
    matching_service = MatchingService(db)
    
    if current_user.role == UserRole.PMI:
        pmi_profile = db.query(PMIProfile).filter(PMIProfile.user_id == current_user.id).first()
        if not pmi_profile:
            return []
        matches = matching_service.get_matches_for_pmi(pmi_profile.id, status)
    
    elif current_user.role == UserRole.PARTNER:
        partner_profile = db.query(PartnerProfile).filter(PartnerProfile.user_id == current_user.id).first()
        if not partner_profile:
            return []
        matches = matching_service.get_matches_for_partner(partner_profile.id, status)
    
    else:
        return []
    
    return matches


# Update Match
@router.put("/matches/{match_id}", response_model=BusinessMatchResponse)
def update_match(
    match_id: int,
    request: MatchUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aggiorna un match esistente (status, note, rating).
    """
    match = db.query(BusinessMatch).filter(BusinessMatch.id == match_id).first()
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match non trovato"
        )
    
    # Verifica permessi
    if current_user.role == UserRole.PMI:
        pmi_profile = db.query(PMIProfile).filter(PMIProfile.user_id == current_user.id).first()
        if not pmi_profile or match.pmi_id != pmi_profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso negato")
        
        if request.notes:
            match.pmi_notes = request.notes
        if request.rating:
            match.pmi_rating = request.rating
    
    elif current_user.role == UserRole.PARTNER:
        partner_profile = db.query(PartnerProfile).filter(PartnerProfile.user_id == current_user.id).first()
        if not partner_profile or match.partner_id != partner_profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso negato")
        
        if request.notes:
            match.partner_notes = request.notes
        if request.rating:
            match.partner_rating = request.rating
    
    if request.status:
        match.status = request.status
    
    db.commit()
    db.refresh(match)
    
    return match


# Meetings
@router.get("/meetings", response_model=MeetingListResponse)
def get_meetings(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ottiene tutti i meeting dell'utente corrente.
    """
    query = db.query(Meeting)
    
    if current_user.role == UserRole.PMI:
        pmi_profile = db.query(PMIProfile).filter(PMIProfile.user_id == current_user.id).first()
        if not pmi_profile:
            return {"total": 0, "items": []}
        query = query.filter(Meeting.pmi_id == pmi_profile.id)
    
    elif current_user.role == UserRole.PARTNER:
        partner_profile = db.query(PartnerProfile).filter(PartnerProfile.user_id == current_user.id).first()
        if not partner_profile:
            return {"total": 0, "items": []}
        query = query.filter(Meeting.partner_id == partner_profile.id)
    
    if status:
        query = query.filter(Meeting.status == status)
    
    meetings = query.order_by(Meeting.scheduled_at.desc()).all()
    
    return {
        "total": len(meetings),
        "items": meetings
    }


@router.post("/meetings", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting(
    meeting_data: MeetingCreate,
    current_user: User = Depends(require_pmi),
    db: Session = Depends(get_db)
):
    """
    Crea un nuovo meeting con un partner.
    """
    pmi_profile = db.query(PMIProfile).filter(PMIProfile.user_id == current_user.id).first()
    
    if not pmi_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profilo PMI non trovato"
        )
    
    # Verifica che il partner esista
    partner_profile = db.query(PartnerProfile).filter(
        PartnerProfile.id == meeting_data.partner_id
    ).first()
    
    if not partner_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner non trovato"
        )
    
    meeting = Meeting(
        pmi_id=pmi_profile.id,
        partner_id=meeting_data.partner_id,
        match_id=meeting_data.match_id,
        title=meeting_data.title,
        description=meeting_data.description,
        scheduled_at=meeting_data.scheduled_at,
        duration_minutes=meeting_data.duration_minutes,
        meeting_platform=meeting_data.meeting_platform,
        status="scheduled"
    )
    
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    
    return meeting


# Messages
@router.get("/messages", response_model=MessageListResponse)
def get_messages(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ottiene tutti i messaggi dell'utente corrente.
    """
    query = db.query(Message).filter(Message.recipient_id == current_user.id)
    
    if unread_only:
        query = query.filter(Message.is_read == False)
    
    messages = query.order_by(Message.created_at.desc()).all()
    unread_count = db.query(Message).filter(
        Message.recipient_id == current_user.id,
        Message.is_read == False
    ).count()
    
    return {
        "total": len(messages),
        "unread_count": unread_count,
        "items": messages
    }


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invia un messaggio a un altro utente.
    """
    # Verifica che il destinatario esista
    recipient = db.query(User).filter(User.id == message_data.recipient_id).first()
    
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destinatario non trovato"
        )
    
    message = Message(
        sender_id=current_user.id,
        recipient_id=message_data.recipient_id,
        subject=message_data.subject,
        body=message_data.body,
        match_id=message_data.match_id,
        meeting_id=message_data.meeting_id
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message


@router.put("/messages/{message_id}/read", response_model=MessageResponse)
def mark_message_as_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Segna un messaggio come letto.
    """
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.recipient_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Messaggio non trovato"
        )
    
    message.is_read = True
    from datetime import datetime
    message.read_at = datetime.utcnow()
    
    db.commit()
    db.refresh(message)
    
    return message

