from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


# ExpoPage Schemas
class ExpoPageBase(BaseModel):
    """Schema base per ExpoPage"""
    title: Optional[str] = Field(None, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    video_url: Optional[str] = None
    theme_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    custom_css: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = None
    keywords: Optional[str] = None
    is_published: bool = False


class ExpoPageCreate(ExpoPageBase):
    """Schema per la creazione di una ExpoPage"""
    pass


class ExpoPageUpdate(ExpoPageBase):
    """Schema per l'aggiornamento di una ExpoPage"""
    pass


class ExpoPageResponse(ExpoPageBase):
    """Schema per la risposta con ExpoPage"""
    id: int
    pmi_id: int
    views_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    """Schema base per Product"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    specifications: Optional[str] = None  # JSON string
    certifications: Optional[str] = None  # JSON string
    main_image_url: Optional[str] = None
    images_urls: Optional[str] = None  # JSON array
    price: Optional[float] = Field(None, ge=0)
    currency: str = Field(default="EUR", max_length=3)
    price_notes: Optional[str] = None
    keywords: Optional[str] = None  # JSON array
    is_featured: bool = False
    is_active: bool = True


class ProductCreate(ProductBase):
    """Schema per la creazione di un Product"""
    pass


class ProductUpdate(BaseModel):
    """Schema per l'aggiornamento di un Product"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    specifications: Optional[str] = None
    certifications: Optional[str] = None
    main_image_url: Optional[str] = None
    images_urls: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = None
    price_notes: Optional[str] = None
    keywords: Optional[str] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema per la risposta con Product"""
    id: int
    pmi_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema per la lista paginata di prodotti"""
    total: int
    page: int
    page_size: int
    items: List[ProductResponse]


# MediaItem Schemas
class MediaItemBase(BaseModel):
    """Schema base per MediaItem"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    media_type: str = Field(..., max_length=50)  # image, video
    url: str = Field(..., max_length=500)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    order_index: int = Field(default=0)


class MediaItemCreate(MediaItemBase):
    """Schema per la creazione di un MediaItem"""
    pass


class MediaItemUpdate(BaseModel):
    """Schema per l'aggiornamento di un MediaItem"""
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None


class MediaItemResponse(MediaItemBase):
    """Schema per la risposta con MediaItem"""
    id: int
    expo_page_id: int
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Document Schemas
class DocumentBase(BaseModel):
    """Schema base per Document"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    file_url: str = Field(..., max_length=500)
    file_name: Optional[str] = Field(None, max_length=255)


class DocumentCreate(DocumentBase):
    """Schema per la creazione di un Document"""
    pass


class DocumentUpdate(BaseModel):
    """Schema per l'aggiornamento di un Document"""
    title: Optional[str] = None
    description: Optional[str] = None


class DocumentResponse(DocumentBase):
    """Schema per la risposta con Document"""
    id: int
    expo_page_id: int
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    downloads_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# File Upload Response
class FileUploadResponse(BaseModel):
    """Schema per la risposta di upload file"""
    url: str
    filename: str
    size: int
    mime_type: str

