from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


# MarketReport Schemas
class MarketReportBase(BaseModel):
    """Schema base per MarketReport"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    summary: Optional[str] = None
    country: Optional[str] = Field(None, max_length=100)
    sector: Optional[str] = Field(None, max_length=100)
    report_type: Optional[str] = Field(None, max_length=50)
    cover_image_url: Optional[str] = None
    file_url: Optional[str] = None
    author: Optional[str] = Field(None, max_length=255)
    publication_date: Optional[datetime] = None
    is_premium: bool = False


class MarketReportCreate(MarketReportBase):
    """Schema per la creazione di un MarketReport"""
    pass


class MarketReportUpdate(BaseModel):
    """Schema per l'aggiornamento di un MarketReport"""
    title: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    country: Optional[str] = None
    sector: Optional[str] = None
    is_premium: Optional[bool] = None


class MarketReportResponse(MarketReportBase):
    """Schema per la risposta con MarketReport"""
    id: int
    views_count: int
    downloads_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MarketReportListResponse(BaseModel):
    """Schema per la lista paginata di report"""
    total: int
    page: int
    page_size: int
    items: List[MarketReportResponse]


# NewsItem Schemas
class NewsItemBase(BaseModel):
    """Schema base per NewsItem"""
    title: str = Field(..., min_length=1, max_length=500)
    summary: Optional[str] = None
    url: str = Field(..., max_length=1000)
    image_url: Optional[str] = Field(None, max_length=500)
    country: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    source: Optional[str] = Field(None, max_length=255)
    published_at: Optional[datetime] = None


class NewsItemCreate(NewsItemBase):
    """Schema per la creazione di un NewsItem"""
    pass


class NewsItemResponse(NewsItemBase):
    """Schema per la risposta con NewsItem"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class NewsItemListResponse(BaseModel):
    """Schema per la lista paginata di notizie"""
    total: int
    page: int
    page_size: int
    items: List[NewsItemResponse]


# Alert Schemas
class AlertBase(BaseModel):
    """Schema base per Alert"""
    name: str = Field(..., min_length=1, max_length=255)
    keywords: Optional[str] = None  # JSON array
    countries: Optional[str] = None  # JSON array
    sectors: Optional[str] = None  # JSON array
    alert_types: Optional[str] = None  # JSON array: news, tenders, reports
    email_notification: bool = True
    frequency: str = Field(default="daily", max_length=20)  # immediate, daily, weekly
    is_active: bool = True


class AlertCreate(AlertBase):
    """Schema per la creazione di un Alert"""
    pass


class AlertUpdate(BaseModel):
    """Schema per l'aggiornamento di un Alert"""
    name: Optional[str] = None
    keywords: Optional[str] = None
    countries: Optional[str] = None
    sectors: Optional[str] = None
    alert_types: Optional[str] = None
    email_notification: Optional[bool] = None
    frequency: Optional[str] = None
    is_active: Optional[bool] = None


class AlertResponse(AlertBase):
    """Schema per la risposta con Alert"""
    id: int
    user_id: int
    last_triggered_at: Optional[datetime] = None
    triggers_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """Schema per la lista di alert"""
    total: int
    items: List[AlertResponse]

