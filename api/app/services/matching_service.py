"""
Servizio per il Business Matching con integrazione algoritmo IA
"""

from sqlalchemy.orm import Session
from typing import List, Dict
import json
import sys
from pathlib import Path

# Aggiungi il path ai modelli IA
ai_models_path = Path(__file__).parent.parent.parent.parent / "ai_models"
sys.path.insert(0, str(ai_models_path))

from matching_algorithm import BusinessMatchingEngine

from ..models.user import PMIProfile, PartnerProfile
from ..models.business import BusinessMatch, MatchStatus


class MatchingService:
    """
    Servizio per gestire il business matching tra PMI e Partner.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.engine = BusinessMatchingEngine()
    
    def _prepare_pmi_data(self, pmi_profile: PMIProfile) -> Dict:
        """
        Prepara i dati della PMI per l'algoritmo di matching.
        """
        # Parse JSON fields
        try:
            target_markets = json.loads(pmi_profile.target_markets) if pmi_profile.target_markets else []
        except:
            target_markets = []
        
        try:
            business_objectives = pmi_profile.business_objectives or ""
        except:
            business_objectives = ""
        
        return {
            'id': pmi_profile.id,
            'company_name': pmi_profile.company_name,
            'sector': pmi_profile.sector or '',
            'target_markets': target_markets,
            'business_needs': ['distributor', 'logistics'],  # Da implementare con campo dedicato
            'company_size': pmi_profile.company_size or 'small',
            'production_capacity': pmi_profile.production_capacity or 'medium',
            'business_objectives': business_objectives
        }
    
    def _prepare_partner_data(self, partner_profile: PartnerProfile) -> Dict:
        """
        Prepara i dati del Partner per l'algoritmo di matching.
        """
        # Parse JSON fields
        try:
            services_offered = json.loads(partner_profile.services_offered) if partner_profile.services_offered else []
        except:
            services_offered = []
        
        try:
            sectors_expertise = json.loads(partner_profile.sectors_expertise) if partner_profile.sectors_expertise else []
        except:
            sectors_expertise = []
        
        return {
            'id': partner_profile.id,
            'company_name': partner_profile.company_name,
            'country': partner_profile.country or '',
            'city': partner_profile.city or '',
            'partner_type': partner_profile.partner_type or '',
            'sectors_expertise': sectors_expertise,
            'services_offered': services_offered,
            'description': partner_profile.description or ''
        }
    
    def find_matches_for_pmi(self, pmi_id: int, limit: int = 10) -> List[Dict]:
        """
        Trova i migliori match per una PMI.
        
        Args:
            pmi_id: ID del profilo PMI
            limit: Numero massimo di match da restituire
        
        Returns:
            Lista di match con score e spiegazioni
        """
        # Carica profilo PMI
        pmi_profile = self.db.query(PMIProfile).filter(PMIProfile.id == pmi_id).first()
        if not pmi_profile:
            return []
        
        # Carica tutti i partner attivi e pubblici
        partners = self.db.query(PartnerProfile).filter(
            PartnerProfile.is_public == True
        ).all()
        
        if not partners:
            return []
        
        # Prepara dati per l'algoritmo
        pmi_data = self._prepare_pmi_data(pmi_profile)
        partners_data = [self._prepare_partner_data(p) for p in partners]
        
        # Esegui matching
        matches = self.engine.find_best_matches(pmi_data, partners_data, top_n=limit)
        
        return matches
    
    def create_match(self, pmi_id: int, partner_id: int, score: float, reason: str) -> BusinessMatch:
        """
        Crea un nuovo match tra PMI e Partner.
        
        Args:
            pmi_id: ID del profilo PMI
            partner_id: ID del profilo Partner
            score: Score di compatibilità
            reason: Spiegazione del match
        
        Returns:
            BusinessMatch creato
        """
        # Verifica se esiste già un match
        existing_match = self.db.query(BusinessMatch).filter(
            BusinessMatch.pmi_id == pmi_id,
            BusinessMatch.partner_id == partner_id
        ).first()
        
        if existing_match:
            return existing_match
        
        # Crea nuovo match
        match = BusinessMatch(
            pmi_id=pmi_id,
            partner_id=partner_id,
            match_score=score,
            match_reason=reason,
            status=MatchStatus.SUGGESTED
        )
        
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)
        
        return match
    
    def accept_match(self, match_id: int, user_role: str, notes: str = None) -> BusinessMatch:
        """
        Accetta un match suggerito.
        
        Args:
            match_id: ID del match
            user_role: Ruolo dell'utente che accetta (pmi o partner)
            notes: Note opzionali
        
        Returns:
            BusinessMatch aggiornato
        """
        match = self.db.query(BusinessMatch).filter(BusinessMatch.id == match_id).first()
        
        if not match:
            return None
        
        match.status = MatchStatus.ACCEPTED
        
        if user_role == 'pmi' and notes:
            match.pmi_notes = notes
        elif user_role == 'partner' and notes:
            match.partner_notes = notes
        
        self.db.commit()
        self.db.refresh(match)
        
        return match
    
    def reject_match(self, match_id: int, user_role: str, notes: str = None) -> BusinessMatch:
        """
        Rifiuta un match suggerito.
        
        Args:
            match_id: ID del match
            user_role: Ruolo dell'utente che rifiuta
            notes: Note opzionali
        
        Returns:
            BusinessMatch aggiornato
        """
        match = self.db.query(BusinessMatch).filter(BusinessMatch.id == match_id).first()
        
        if not match:
            return None
        
        match.status = MatchStatus.REJECTED
        
        if user_role == 'pmi' and notes:
            match.pmi_notes = notes
        elif user_role == 'partner' and notes:
            match.partner_notes = notes
        
        self.db.commit()
        self.db.refresh(match)
        
        return match
    
    def get_matches_for_pmi(self, pmi_id: int, status: MatchStatus = None) -> List[BusinessMatch]:
        """
        Ottiene tutti i match di una PMI, opzionalmente filtrati per status.
        
        Args:
            pmi_id: ID del profilo PMI
            status: Status opzionale per filtrare
        
        Returns:
            Lista di BusinessMatch
        """
        query = self.db.query(BusinessMatch).filter(BusinessMatch.pmi_id == pmi_id)
        
        if status:
            query = query.filter(BusinessMatch.status == status)
        
        return query.order_by(BusinessMatch.match_score.desc()).all()
    
    def get_matches_for_partner(self, partner_id: int, status: MatchStatus = None) -> List[BusinessMatch]:
        """
        Ottiene tutti i match di un Partner, opzionalmente filtrati per status.
        
        Args:
            partner_id: ID del profilo Partner
            status: Status opzionale per filtrare
        
        Returns:
            Lista di BusinessMatch
        """
        query = self.db.query(BusinessMatch).filter(BusinessMatch.partner_id == partner_id)
        
        if status:
            query = query.filter(BusinessMatch.status == status)
        
        return query.order_by(BusinessMatch.match_score.desc()).all()

