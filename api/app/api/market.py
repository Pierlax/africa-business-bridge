from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..core.database import get_db
from ..core.dependencies import get_current_user, require_roles
from ..models.user import User, UserRole
from ..models.business import MarketReport, NewsItem, Alert
from ..schemas.market import (
    MarketReportCreate,
    MarketReportUpdate,
    MarketReportResponse,
    MarketReportListResponse,
    NewsItemCreate,
    NewsItemResponse,
    NewsItemListResponse,
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertListResponse
)
from ..services.news_scraper import NewsScraperService

router = APIRouter(prefix="/market", tags=["Market Intelligence"])


# Market Reports
@router.get("/reports", response_model=MarketReportListResponse)
def list_reports(
    country: Optional[str] = None,
    sector: Optional[str] = None,
    report_type: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista i report di mercato disponibili con filtri opzionali.
    """
    query = db.query(MarketReport)
    
    if country:
        query = query.filter(MarketReport.country == country)
    if sector:
        query = query.filter(MarketReport.sector == sector)
    if report_type:
        query = query.filter(MarketReport.report_type == report_type)
    
    total = query.count()
    
    # Paginazione
    offset = (page - 1) * page_size
    reports = query.order_by(MarketReport.publication_date.desc()).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": reports
    }


@router.get("/reports/{report_id}", response_model=MarketReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """
    Ottiene un report specifico e incrementa il contatore visualizzazioni.
    """
    report = db.query(MarketReport).filter(MarketReport.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report non trovato"
        )
    
    # Incrementa visualizzazioni
    report.views_count += 1
    db.commit()
    
    return report


@router.post("/reports", response_model=MarketReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    report_data: MarketReportCreate,
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Crea un nuovo report di mercato (solo admin).
    """
    report = MarketReport(**report_data.model_dump())
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report


@router.put("/reports/{report_id}", response_model=MarketReportResponse)
def update_report(
    report_id: int,
    report_data: MarketReportUpdate,
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Aggiorna un report esistente (solo admin).
    """
    report = db.query(MarketReport).filter(MarketReport.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report non trovato"
        )
    
    for field, value in report_data.model_dump(exclude_unset=True).items():
        setattr(report, field, value)
    
    db.commit()
    db.refresh(report)
    
    return report


# News
@router.get("/news", response_model=NewsItemListResponse)
def list_news(
    country: Optional[str] = None,
    category: Optional[str] = None,
    source: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    refresh: bool = Query(default=False, description="Forza refresh da scraper"),
    db: Session = Depends(get_db)
):
    """
    Lista le notizie dai mercati target con filtri opzionali.
    Se refresh=true, esegue scraping in tempo reale.
    """
    # Se richiesto refresh, scrape nuove notizie
    if refresh:
        scraper = NewsScraperService()
        countries_filter = [country] if country else None
        scraped_news = scraper.scrape_all_sources(countries_filter, limit=50)
        
        # Salva notizie nel database (evita duplicati)
        for news_data in scraped_news:
            existing = db.query(NewsItem).filter(NewsItem.url == news_data['url']).first()
            if not existing:
                news_item = NewsItem(
                    title=news_data['title'],
                    summary=news_data.get('summary'),
                    url=news_data['url'],
                    image_url=news_data.get('image_url'),
                    country=news_data.get('country'),
                    category=news_data.get('category'),
                    source=news_data.get('source'),
                    published_at=news_data.get('published_at')
                )
                db.add(news_item)
        
        db.commit()
    
    # Query dal database
    query = db.query(NewsItem)
    
    if country:
        query = query.filter(NewsItem.country == country)
    if category:
        query = query.filter(NewsItem.category == category)
    if source:
        query = query.filter(NewsItem.source == source)
    
    total = query.count()
    
    # Paginazione
    offset = (page - 1) * page_size
    news = query.order_by(NewsItem.published_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": news
    }


@router.post("/news", response_model=NewsItemResponse, status_code=status.HTTP_201_CREATED)
def create_news(
    news_data: NewsItemCreate,
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Aggiunge manualmente una notizia (solo admin).
    """
    # Verifica duplicati
    existing = db.query(NewsItem).filter(NewsItem.url == news_data.url).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notizia già esistente"
        )
    
    news_item = NewsItem(**news_data.model_dump())
    
    db.add(news_item)
    db.commit()
    db.refresh(news_item)
    
    return news_item


# Alerts
@router.get("/alerts", response_model=AlertListResponse)
def list_my_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista tutti gli alert dell'utente corrente.
    """
    alerts = db.query(Alert).filter(Alert.user_id == current_user.id).all()
    
    return {
        "total": len(alerts),
        "items": alerts
    }


@router.post("/alerts", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea un nuovo alert personalizzato.
    """
    alert = Alert(
        user_id=current_user.id,
        **alert_data.model_dump()
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    return alert


@router.put("/alerts/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aggiorna un alert esistente.
    """
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert non trovato"
        )
    
    for field, value in alert_data.model_dump(exclude_unset=True).items():
        setattr(alert, field, value)
    
    db.commit()
    db.refresh(alert)
    
    return alert


@router.delete("/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina un alert.
    """
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert non trovato"
        )
    
    db.delete(alert)
    db.commit()
    
    return None


# Search endpoint
@router.get("/search")
def search_market_intelligence(
    q: str = Query(..., min_length=2, description="Query di ricerca"),
    type: str = Query(default="all", description="Tipo: all, reports, news"),
    country: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Cerca tra report e notizie.
    """
    results = {
        "query": q,
        "reports": [],
        "news": []
    }
    
    # Cerca nei report
    if type in ["all", "reports"]:
        reports_query = db.query(MarketReport).filter(
            (MarketReport.title.ilike(f"%{q}%")) |
            (MarketReport.description.ilike(f"%{q}%")) |
            (MarketReport.summary.ilike(f"%{q}%"))
        )
        
        if country:
            reports_query = reports_query.filter(MarketReport.country == country)
        
        results["reports"] = reports_query.limit(limit).all()
    
    # Cerca nelle notizie
    if type in ["all", "news"]:
        news_query = db.query(NewsItem).filter(
            (NewsItem.title.ilike(f"%{q}%")) |
            (NewsItem.summary.ilike(f"%{q}%"))
        )
        
        if country:
            news_query = news_query.filter(NewsItem.country == country)
        
        results["news"] = news_query.limit(limit).all()
    
    return results

