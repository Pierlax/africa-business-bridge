"""
Algoritmo di Business Matching con IA per Africa Business Bridge

Questo modulo implementa l'algoritmo di matching tra PMI italiane e Partner Locali
basandosi su diversi fattori di compatibilità.
"""

import numpy as np
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json


class BusinessMatchingEngine:
    """
    Engine per il matching intelligente tra PMI e Partner Locali.
    
    L'algoritmo considera:
    - Settore merceologico (40% del peso)
    - Paese target (25% del peso)
    - Tipo di servizio richiesto (20% del peso)
    - Dimensione aziendale e capacità (10% del peso)
    - Keywords e obiettivi (5% del peso)
    """
    
    def __init__(self):
        self.sector_weight = 0.40
        self.country_weight = 0.25
        self.service_weight = 0.20
        self.size_weight = 0.10
        self.keyword_weight = 0.05
        
        # Mapping settori compatibili
        self.sector_compatibility = {
            'agritech': ['agriculture', 'food_processing', 'logistics'],
            'manufacturing': ['industrial', 'logistics', 'quality_control'],
            'technology': ['it_services', 'consulting', 'innovation'],
            'food_beverage': ['food_processing', 'distribution', 'retail'],
            'fashion': ['textile', 'retail', 'distribution'],
            'construction': ['engineering', 'real_estate', 'logistics'],
            'energy': ['renewable_energy', 'engineering', 'consulting'],
            'healthcare': ['medical_devices', 'pharmaceuticals', 'distribution'],
        }
        
        # Vectorizer per analisi testuale
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    
    def calculate_sector_score(self, pmi_sector: str, partner_sectors: List[str]) -> float:
        """
        Calcola il punteggio di compatibilità settoriale.
        
        Args:
            pmi_sector: Settore della PMI
            partner_sectors: Lista dei settori di expertise del partner
        
        Returns:
            Score da 0 a 1
        """
        if not pmi_sector or not partner_sectors:
            return 0.0
        
        # Match esatto
        if pmi_sector in partner_sectors:
            return 1.0
        
        # Match con settori compatibili
        compatible_sectors = self.sector_compatibility.get(pmi_sector, [])
        for sector in partner_sectors:
            if sector in compatible_sectors:
                return 0.7
        
        return 0.0
    
    def calculate_country_score(self, pmi_targets: List[str], partner_country: str) -> float:
        """
        Calcola il punteggio di compatibilità geografica.
        
        Args:
            pmi_targets: Lista dei paesi target della PMI
            partner_country: Paese del partner
        
        Returns:
            Score da 0 a 1
        """
        if not pmi_targets or not partner_country:
            return 0.0
        
        # Match esatto
        if partner_country in pmi_targets:
            return 1.0
        
        # Paesi limitrofi (bonus per vicinanza geografica)
        neighboring_countries = {
            'Kenya': ['Tanzania', 'Uganda'],
            'Tanzania': ['Kenya', 'Uganda'],
            'Ethiopia': ['Kenya', 'Sudan'],
        }
        
        neighbors = neighboring_countries.get(partner_country, [])
        for target in pmi_targets:
            if target in neighbors:
                return 0.5
        
        return 0.0
    
    def calculate_service_score(self, pmi_needs: List[str], partner_services: List[str]) -> float:
        """
        Calcola il punteggio di compatibilità dei servizi.
        
        Args:
            pmi_needs: Esigenze della PMI (es. 'distributor', 'legal', 'logistics')
            partner_services: Servizi offerti dal partner
        
        Returns:
            Score da 0 a 1
        """
        if not pmi_needs or not partner_services:
            return 0.0
        
        # Conta quanti servizi richiesti sono offerti
        matches = sum(1 for need in pmi_needs if need in partner_services)
        
        if matches == 0:
            return 0.0
        
        # Normalizza in base al numero di esigenze
        return min(matches / len(pmi_needs), 1.0)
    
    def calculate_size_score(self, pmi_size: str, pmi_capacity: str, partner_type: str) -> float:
        """
        Calcola il punteggio di compatibilità dimensionale.
        
        Args:
            pmi_size: Dimensione PMI (micro, piccola, media)
            pmi_capacity: Capacità produttiva
            partner_type: Tipo di partner
        
        Returns:
            Score da 0 a 1
        """
        # Mapping dimensioni compatibili
        size_compatibility = {
            'micro': ['small_distributor', 'consultant', 'agent'],
            'small': ['small_distributor', 'medium_distributor', 'consultant'],
            'medium': ['medium_distributor', 'large_distributor', 'logistics_company'],
        }
        
        if not pmi_size or not partner_type:
            return 0.5  # Score neutro se mancano dati
        
        compatible_types = size_compatibility.get(pmi_size, [])
        return 1.0 if partner_type in compatible_types else 0.3
    
    def calculate_keyword_score(self, pmi_objectives: str, partner_description: str) -> float:
        """
        Calcola il punteggio di similarità testuale usando TF-IDF.
        
        Args:
            pmi_objectives: Obiettivi di business della PMI
            partner_description: Descrizione del partner
        
        Returns:
            Score da 0 a 1
        """
        if not pmi_objectives or not partner_description:
            return 0.0
        
        try:
            # Crea matrice TF-IDF
            tfidf_matrix = self.vectorizer.fit_transform([pmi_objectives, partner_description])
            
            # Calcola similarità coseno
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except:
            return 0.0
    
    def calculate_match_score(self, pmi_data: Dict, partner_data: Dict) -> Tuple[float, Dict]:
        """
        Calcola il punteggio totale di matching tra una PMI e un Partner.
        
        Args:
            pmi_data: Dizionario con i dati della PMI
            partner_data: Dizionario con i dati del Partner
        
        Returns:
            Tupla (score totale, breakdown dei punteggi)
        """
        # Calcola i punteggi individuali
        sector_score = self.calculate_sector_score(
            pmi_data.get('sector', ''),
            partner_data.get('sectors_expertise', [])
        )
        
        country_score = self.calculate_country_score(
            pmi_data.get('target_markets', []),
            partner_data.get('country', '')
        )
        
        service_score = self.calculate_service_score(
            pmi_data.get('business_needs', []),
            partner_data.get('services_offered', [])
        )
        
        size_score = self.calculate_size_score(
            pmi_data.get('company_size', ''),
            pmi_data.get('production_capacity', ''),
            partner_data.get('partner_type', '')
        )
        
        keyword_score = self.calculate_keyword_score(
            pmi_data.get('business_objectives', ''),
            partner_data.get('description', '')
        )
        
        # Calcola score totale pesato
        total_score = (
            sector_score * self.sector_weight +
            country_score * self.country_weight +
            service_score * self.service_weight +
            size_score * self.size_weight +
            keyword_score * self.keyword_weight
        )
        
        # Crea breakdown dettagliato
        breakdown = {
            'sector_score': round(sector_score * 100, 2),
            'country_score': round(country_score * 100, 2),
            'service_score': round(service_score * 100, 2),
            'size_score': round(size_score * 100, 2),
            'keyword_score': round(keyword_score * 100, 2),
            'total_score': round(total_score * 100, 2)
        }
        
        return total_score, breakdown
    
    def generate_match_explanation(self, breakdown: Dict, pmi_data: Dict, partner_data: Dict) -> str:
        """
        Genera una spiegazione testuale del match.
        
        Args:
            breakdown: Breakdown dei punteggi
            pmi_data: Dati della PMI
            partner_data: Dati del Partner
        
        Returns:
            Testo esplicativo del match
        """
        explanations = []
        
        # Settore
        if breakdown['sector_score'] >= 70:
            explanations.append(
                f"Il partner ha esperienza nel settore {pmi_data.get('sector', 'richiesto')}"
            )
        
        # Paese
        if breakdown['country_score'] >= 70:
            explanations.append(
                f"Il partner opera in {partner_data.get('country', '')}, uno dei vostri mercati target"
            )
        
        # Servizi
        if breakdown['service_score'] >= 70:
            explanations.append(
                "Il partner offre i servizi di cui avete bisogno"
            )
        
        # Dimensione
        if breakdown['size_score'] >= 70:
            explanations.append(
                "La dimensione del partner è compatibile con la vostra azienda"
            )
        
        if not explanations:
            explanations.append("Questo partner potrebbe essere interessante per la vostra espansione")
        
        return ". ".join(explanations) + "."
    
    def find_best_matches(self, pmi_data: Dict, partners_data: List[Dict], top_n: int = 10) -> List[Dict]:
        """
        Trova i migliori match per una PMI tra una lista di partner.
        
        Args:
            pmi_data: Dati della PMI
            partners_data: Lista di dizionari con dati dei partner
            top_n: Numero di match da restituire
        
        Returns:
            Lista di match ordinati per score decrescente
        """
        matches = []
        
        for partner in partners_data:
            score, breakdown = self.calculate_match_score(pmi_data, partner)
            
            # Genera spiegazione
            explanation = self.generate_match_explanation(breakdown, pmi_data, partner)
            
            matches.append({
                'partner_id': partner.get('id'),
                'partner_name': partner.get('company_name'),
                'match_score': breakdown['total_score'],
                'breakdown': breakdown,
                'explanation': explanation,
                'partner_data': partner
            })
        
        # Ordina per score decrescente
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Restituisci top N
        return matches[:top_n]


# Esempio di utilizzo
if __name__ == "__main__":
    # Inizializza engine
    engine = BusinessMatchingEngine()
    
    # Dati di esempio PMI
    pmi = {
        'id': 1,
        'company_name': 'Italian Agritech SRL',
        'sector': 'agritech',
        'target_markets': ['Kenya', 'Tanzania'],
        'business_needs': ['distributor', 'logistics'],
        'company_size': 'small',
        'production_capacity': 'medium',
        'business_objectives': 'Espandere la distribuzione di macchinari agricoli in Africa orientale'
    }
    
    # Dati di esempio Partner
    partners = [
        {
            'id': 101,
            'company_name': 'Nairobi Agro Distribution',
            'country': 'Kenya',
            'partner_type': 'medium_distributor',
            'sectors_expertise': ['agriculture', 'logistics'],
            'services_offered': ['distributor', 'logistics', 'warehousing'],
            'description': 'Leading agricultural equipment distributor in East Africa with 15 years experience'
        },
        {
            'id': 102,
            'company_name': 'Tanzania Tech Solutions',
            'country': 'Tanzania',
            'partner_type': 'consultant',
            'sectors_expertise': ['technology', 'consulting'],
            'services_offered': ['consulting', 'market_research'],
            'description': 'Technology consulting firm specializing in market entry strategies'
        }
    ]
    
    # Trova i match
    matches = engine.find_best_matches(pmi, partners, top_n=5)
    
    # Stampa risultati
    print("=== Business Matching Results ===\n")
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match['partner_name']}")
        print(f"   Match Score: {match['match_score']}%")
        print(f"   Explanation: {match['explanation']}")
        print(f"   Breakdown: {match['breakdown']}")
        print()

