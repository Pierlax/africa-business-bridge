"""
Servizio per lo scraping automatico di notizie dai mercati target
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class NewsScraperService:
    """
    Servizio per aggregare notizie da fonti predefinite.
    
    Fonti supportate:
    - ICE (Istituto per il Commercio Estero)
    - SACE
    - InfoMercatiEsteri
    - Business Daily Africa
    - The East African
    """
    
    def __init__(self):
        self.sources = {
            'ice': {
                'name': 'ICE - Istituto Commercio Estero',
                'url': 'https://www.ice.it/it/news',
                'enabled': True
            },
            'sace': {
                'name': 'SACE',
                'url': 'https://www.sace.it/media/news',
                'enabled': True
            },
            'infomercati': {
                'name': 'InfoMercatiEsteri',
                'url': 'https://www.infomercatiesteri.it/news.php',
                'enabled': True
            },
            'business_daily_africa': {
                'name': 'Business Daily Africa',
                'url': 'https://www.businessdailyafrica.com',
                'enabled': True
            }
        }
    
    def scrape_all_sources(self, countries: List[str] = None, limit: int = 50) -> List[Dict]:
        """
        Scrape notizie da tutte le fonti abilitate.
        
        Args:
            countries: Lista di paesi da filtrare (Kenya, Tanzania, Ethiopia)
            limit: Numero massimo di notizie per fonte
        
        Returns:
            Lista di notizie aggregate
        """
        all_news = []
        
        for source_key, source_info in self.sources.items():
            if not source_info['enabled']:
                continue
            
            try:
                news = self._scrape_source(source_key, source_info, countries, limit)
                all_news.extend(news)
                logger.info(f"Scraped {len(news)} news from {source_info['name']}")
            except Exception as e:
                logger.error(f"Error scraping {source_info['name']}: {str(e)}")
        
        # Ordina per data di pubblicazione
        all_news.sort(key=lambda x: x.get('published_at', datetime.min), reverse=True)
        
        return all_news
    
    def _scrape_source(self, source_key: str, source_info: Dict, countries: List[str], limit: int) -> List[Dict]:
        """
        Scrape notizie da una fonte specifica.
        
        Nota: Questa è una implementazione di esempio.
        In produzione, ogni fonte richiede un parser specifico.
        """
        news = []
        
        # Implementazione di esempio con dati mock
        # In produzione, sostituire con vero scraping
        
        if source_key == 'ice':
            news = self._scrape_ice(countries, limit)
        elif source_key == 'business_daily_africa':
            news = self._scrape_business_daily(countries, limit)
        else:
            # Per altre fonti, usa dati di esempio
            news = self._generate_mock_news(source_info['name'], countries, limit)
        
        return news
    
    def _scrape_ice(self, countries: List[str], limit: int) -> List[Dict]:
        """
        Scrape notizie da ICE.
        
        Nota: Implementazione mock. In produzione, usare vero scraping.
        """
        # Mock data per demo
        mock_news = [
            {
                'title': 'Kenya: Nuove opportunità nel settore agritech',
                'summary': 'Il governo keniano ha annunciato incentivi per investimenti esteri nel settore agricolo tecnologico.',
                'url': 'https://www.ice.it/it/news/kenya-agritech-2024',
                'source': 'ICE',
                'country': 'Kenya',
                'category': 'economy',
                'published_at': datetime.now() - timedelta(days=1)
            },
            {
                'title': 'Tanzania: Crescita del PIL al 5.2% nel 2024',
                'summary': 'La Tanzania registra una crescita economica robusta trainata da agricoltura e turismo.',
                'url': 'https://www.ice.it/it/news/tanzania-pil-2024',
                'source': 'ICE',
                'country': 'Tanzania',
                'category': 'economy',
                'published_at': datetime.now() - timedelta(days=2)
            },
            {
                'title': 'Etiopia: Nuovi accordi commerciali con l\'UE',
                'summary': 'L\'Etiopia firma accordi preferenziali per l\'export verso mercati europei.',
                'url': 'https://www.ice.it/it/news/etiopia-accordi-ue-2024',
                'source': 'ICE',
                'country': 'Ethiopia',
                'category': 'trade',
                'published_at': datetime.now() - timedelta(days=3)
            }
        ]
        
        # Filtra per paesi se specificato
        if countries:
            mock_news = [n for n in mock_news if n['country'] in countries]
        
        return mock_news[:limit]
    
    def _scrape_business_daily(self, countries: List[str], limit: int) -> List[Dict]:
        """
        Scrape notizie da Business Daily Africa.
        
        Nota: Implementazione mock. In produzione, usare vero scraping.
        """
        mock_news = [
            {
                'title': 'East Africa: Regional trade bloc expands',
                'summary': 'The East African Community announces new member states joining the trade bloc.',
                'url': 'https://www.businessdailyafrica.com/bd/economy/eac-expansion-2024',
                'source': 'Business Daily Africa',
                'country': 'Kenya',
                'category': 'trade',
                'published_at': datetime.now() - timedelta(hours=12)
            },
            {
                'title': 'Kenya: Tech startups attract $200M in funding',
                'summary': 'Kenyan technology sector sees record investment from international venture capital.',
                'url': 'https://www.businessdailyafrica.com/bd/markets/tech-funding-2024',
                'source': 'Business Daily Africa',
                'country': 'Kenya',
                'category': 'technology',
                'published_at': datetime.now() - timedelta(hours=18)
            }
        ]
        
        if countries:
            mock_news = [n for n in mock_news if n['country'] in countries]
        
        return mock_news[:limit]
    
    def _generate_mock_news(self, source_name: str, countries: List[str], limit: int) -> List[Dict]:
        """
        Genera notizie mock per fonti non ancora implementate.
        """
        target_countries = countries if countries else ['Kenya', 'Tanzania', 'Ethiopia']
        
        news = []
        for i, country in enumerate(target_countries[:limit]):
            news.append({
                'title': f'{country}: Aggiornamento economico da {source_name}',
                'summary': f'Notizia di esempio da {source_name} riguardante {country}.',
                'url': f'https://example.com/news/{country.lower()}-{i}',
                'source': source_name,
                'country': country,
                'category': 'economy',
                'published_at': datetime.now() - timedelta(days=i+1)
            })
        
        return news
    
    def search_news(self, keywords: List[str], countries: List[str] = None, days_back: int = 30) -> List[Dict]:
        """
        Cerca notizie per keywords specifiche.
        
        Args:
            keywords: Lista di parole chiave da cercare
            countries: Lista di paesi da filtrare
            days_back: Numero di giorni indietro da cercare
        
        Returns:
            Lista di notizie che matchano i criteri
        """
        # Scrape tutte le notizie recenti
        all_news = self.scrape_all_sources(countries, limit=100)
        
        # Filtra per keywords
        if keywords:
            filtered_news = []
            for news_item in all_news:
                title_lower = news_item['title'].lower()
                summary_lower = (news_item.get('summary') or '').lower()
                
                for keyword in keywords:
                    if keyword.lower() in title_lower or keyword.lower() in summary_lower:
                        filtered_news.append(news_item)
                        break
            
            all_news = filtered_news
        
        # Filtra per data
        cutoff_date = datetime.now() - timedelta(days=days_back)
        all_news = [n for n in all_news if n.get('published_at', datetime.min) >= cutoff_date]
        
        return all_news


# Funzione helper per uso standalone
def scrape_latest_news(countries: List[str] = None, limit: int = 20) -> List[Dict]:
    """
    Funzione helper per scraping rapido delle ultime notizie.
    """
    scraper = NewsScraperService()
    return scraper.scrape_all_sources(countries, limit)

