from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from pathlib import Path
import mimetypes

from ..core.database import get_db
from ..core.dependencies import get_current_user, require_pmi
from ..models.user import User, PMIProfile
from ..models.expo import ExpoPage, Product, MediaItem, Document
from ..schemas.expo import (
    ExpoPageCreate, ExpoPageUpdate, ExpoPageResponse,
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    MediaItemCreate, MediaItemResponse,
    DocumentCreate, DocumentResponse,
    FileUploadResponse
)
from ..core.config import settings

router = APIRouter(prefix="/expo", tags=["Expo Virtuale"])


# ExpoPage Endpoints
@router.get("/pages/{pmi_id}", response_model=ExpoPageResponse)
def get_expo_page(pmi_id: int, db: Session = Depends(get_db)):
    """
    Ottiene la pagina Expo Virtuale di una PMI (pubblico).
    """
    expo_page = db.query(ExpoPage).filter(ExpoPage.pmi_id == pmi_id).first()
    
    if not expo_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagina Expo non trovata"
        )
    
    # Incrementa contatore visualizzazioni
    expo_page.views_count += 1
    db.commit()
    
    return expo_page


@router.get("/pages/my/page", response_model=ExpoPageResponse)
def get_my_expo_page(
    current_user: User = Depends(require_pmi),
    db: Session = Depends(get_db)
):
    """
    Ottiene la pagina Expo Virtuale della PMI corrente.
    """
    pmi_profile = db.query(PMIProfile).filter(PMIProfile.user_id == current_user.id).first()
    
    if not pmi_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profilo PMI non trovato"
        )
    
    expo_page = db.query(ExpoPage).filter(ExpoPage.pmi_id == pmi_profile.id).first()
    
    if not expo_page:
        # Crea una pagina expo vuota se non esiste
        expo_page = ExpoPage(pmi_id=pmi_profile.id)
        db.add(expo_page)
        db.commit()
        db.refresh(expo_page)
    
    return expo_page


@router.put("/pages/my/page", response_model=ExpoPageResponse)
def update_my_expo_page(
    page_data: ExpoPageUpdate,
    current_user: User = Depends(require_pmi),
    db: Session = Depends(get_db)
):
    """
    Aggiorna la pagina Expo Virtuale della PMI corrente.
    """
    pmi_profile = db.query(PMIProfile).filter(PMIProfile.user_id == current_user.id).first()
    
    if not pmi_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profilo PMI non trovato"
        )
    
    expo_page = db.query(ExpoPage).filter(ExpoPage.pmi_id == pmi_profile.id).first()
    
    if not expo_page:
        expo_page = ExpoPage(pmi_id=pmi_profile.id)
        db.add(expo_page)
    
    # Aggiorna i campi
    for field, value in page_data.model_dump(exclude_unset=True).items():
        setattr(expo_page, field, value)
    
    db.commit()
    db.refresh(expo_page)
    
    return expo_page


# Product Endpoints
@router.get("/products", response_model=ProductListResponse)
def list_products(
    pmi_id: Optional[int] = None,
    category: Optional[str] = None,
    is_featured: Optional[bool] = None,
    is_active: Optional[bool] = True,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """
    Lista i prodotti con filtri opzionali.
    """
    query = db.query(Product)
    
    if pmi_id:
        query = query.filter(Product.pmi_id == pmi_id)
    if category:
        query = query.filter(Product.category == category)
    if is_featured is not None:
        query = query.filter(Product.is_featured == is_featured)
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    total = query.count()
    
    # Paginazione
    offset = (page - 1) * page_size
    products = query.offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": products
    }


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Ottiene un prodotto specifico.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prodotto non trovato"
        )
    
    return product


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_pmi),
    db: Session = Depends(get_db)
):
    """
    Crea un nuovo prodotto.
    """
    pmi_profile = db.query(PMIProfile).filter(PMIProfile.user_id == current_user.id).first()
    
    if not pmi_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profilo PMI non trovato"
        )
    
    product = Product(
        pmi_id=pmi_profile.id,
        **product_data.model_dump()
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(require_pmi),
    db: Session = Depends(get_db)
):
    """
    Aggiorna un prodotto esistente.
    """
    pmi_profile = db.query(PMIProfile).filter(PMIProfile.user_id == current_user.id).first()
    
    if not pmi_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profilo PMI non trovato"
        )
    
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.pmi_id == pmi_profile.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prodotto non trovato"
        )
    
    # Aggiorna i campi
    for field, value in product_data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_user: User = Depends(require_pmi),
    db: Session = Depends(get_db)
):
    """
    Elimina un prodotto.
    """
    pmi_profile = db.query(PMIProfile).filter(PMIProfile.user_id == current_user.id).first()
    
    if not pmi_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profilo PMI non trovato"
        )
    
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.pmi_id == pmi_profile.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prodotto non trovato"
        )
    
    db.delete(product)
    db.commit()
    
    return None


# File Upload Endpoint
@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Form(...),  # logo, banner, product_image, document
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload di file (immagini, documenti).
    """
    # Validazione tipo file
    allowed_types = {
        'logo': ['image/jpeg', 'image/png', 'image/svg+xml'],
        'banner': ['image/jpeg', 'image/png'],
        'product_image': ['image/jpeg', 'image/png'],
        'document': ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    }
    
    if file_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo file non valido"
        )
    
    # Verifica MIME type
    if file.content_type not in allowed_types[file_type]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo MIME non consentito per {file_type}"
        )
    
    # Verifica dimensione file
    file.file.seek(0, 2)  # Vai alla fine del file
    file_size = file.file.tell()
    file.file.seek(0)  # Torna all'inizio
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File troppo grande. Massimo {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    # Crea directory se non esiste
    upload_dir = Path(settings.UPLOAD_DIR) / file_type
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Genera nome file unico
    file_extension = Path(file.filename).suffix
    unique_filename = f"{current_user.id}_{file_type}_{os.urandom(8).hex()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    # Salva il file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il salvataggio del file: {str(e)}"
        )
    
    # Restituisci URL relativo
    relative_url = f"/uploads/{file_type}/{unique_filename}"
    
    return {
        "url": relative_url,
        "filename": unique_filename,
        "size": file_size,
        "mime_type": file.content_type
    }


# MediaItem Endpoints
@router.get("/pages/{pmi_id}/media", response_model=List[MediaItemResponse])
def get_expo_media(pmi_id: int, db: Session = Depends(get_db)):
    """
    Ottiene la gallery media di una pagina Expo.
    """
    expo_page = db.query(ExpoPage).filter(ExpoPage.pmi_id == pmi_id).first()
    
    if not expo_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagina Expo non trovata"
        )
    
    media_items = db.query(MediaItem).filter(
        MediaItem.expo_page_id == expo_page.id
    ).order_by(MediaItem.order_index).all()
    
    return media_items


@router.post("/pages/my/media", response_model=MediaItemResponse, status_code=status.HTTP_201_CREATED)
def add_media_to_expo(
    media_data: MediaItemCreate,
    current_user: User = Depends(require_pmi),
    db: Session = Depends(get_db)
):
    """
    Aggiunge un media item alla gallery della propria pagina Expo.
    """
    pmi_profile = db.query(PMIProfile).filter(PMIProfile.user_id == current_user.id).first()
    
    if not pmi_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profilo PMI non trovato"
        )
    
    expo_page = db.query(ExpoPage).filter(ExpoPage.pmi_id == pmi_profile.id).first()
    
    if not expo_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagina Expo non trovata"
        )
    
    media_item = MediaItem(
        expo_page_id=expo_page.id,
        **media_data.model_dump()
    )
    
    db.add(media_item)
    db.commit()
    db.refresh(media_item)
    
    return media_item


# Document Endpoints
@router.get("/pages/{pmi_id}/documents", response_model=List[DocumentResponse])
def get_expo_documents(pmi_id: int, db: Session = Depends(get_db)):
    """
    Ottiene i documenti di una pagina Expo.
    """
    expo_page = db.query(ExpoPage).filter(ExpoPage.pmi_id == pmi_id).first()
    
    if not expo_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagina Expo non trovata"
        )
    
    documents = db.query(Document).filter(
        Document.expo_page_id == expo_page.id
    ).all()
    
    return documents


@router.post("/pages/my/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def add_document_to_expo(
    document_data: DocumentCreate,
    current_user: User = Depends(require_pmi),
    db: Session = Depends(get_db)
):
    """
    Aggiunge un documento alla propria pagina Expo.
    """
    pmi_profile = db.query(PMIProfile).filter(PMIProfile.user_id == current_user.id).first()
    
    if not pmi_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profilo PMI non trovato"
        )
    
    expo_page = db.query(ExpoPage).filter(ExpoPage.pmi_id == pmi_profile.id).first()
    
    if not expo_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagina Expo non trovata"
        )
    
    document = Document(
        expo_page_id=expo_page.id,
        **document_data.model_dump()
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return document

