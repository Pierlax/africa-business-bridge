# API Documentation - Africa Business Bridge

Documentazione completa delle API REST della piattaforma Africa Business Bridge.

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://api.africabusinessbridge.com/api/v1
```

## Autenticazione

Tutte le API protette richiedono un token JWT nell'header Authorization:

```
Authorization: Bearer <access_token>
```

### Ottenere un Token

**Endpoint**: `POST /auth/login`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Endpoints

### Authentication

#### POST /auth/register
Registra un nuovo utente.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "Mario Rossi",
  "role": "pmi"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Mario Rossi",
  "role": "pmi",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### POST /auth/login
Effettua il login.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST /auth/refresh
Rinnova i token.

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET /auth/me
Ottiene le informazioni dell'utente corrente.

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Mario Rossi",
  "role": "pmi",
  "is_active": true,
  "is_verified": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### POST /auth/change-password
Cambia la password dell'utente.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "old_password": "OldPass123",
  "new_password": "NewSecurePass456"
}
```

**Response**:
```json
{
  "message": "Password aggiornata con successo"
}
```

### User Profiles

#### GET /profiles/pmi/{pmi_id}
Ottiene il profilo di una PMI.

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "id": 1,
  "user_id": 1,
  "company_name": "Italian Agritech SRL",
  "vat_number": "IT12345678901",
  "company_size": "small",
  "sector": "agritech",
  "description": "Produttori di macchinari agricoli innovativi",
  "website": "https://italianagritech.com",
  "phone": "+39 02 1234567",
  "address": "Via Roma 123",
  "city": "Milano",
  "country": "Italia",
  "business_objectives": "Espansione in mercati africani",
  "target_markets": ["Kenya", "Tanzania", "Ethiopia"],
  "production_capacity": "medium"
}
```

#### PUT /profiles/pmi/{pmi_id}
Aggiorna il profilo di una PMI.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "company_name": "Italian Agritech SRL",
  "sector": "agritech",
  "description": "Descrizione aggiornata",
  "target_markets": ["Kenya", "Tanzania"]
}
```

**Response**: Profilo aggiornato (stesso formato del GET)

#### GET /profiles/partner/{partner_id}
Ottiene il profilo di un Partner Locale.

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "id": 1,
  "user_id": 2,
  "company_name": "Nairobi Distribution Ltd",
  "partner_type": "distributor",
  "country": "Kenya",
  "city": "Nairobi",
  "description": "Leading distributor in East Africa",
  "services_offered": ["distribution", "logistics", "warehousing"],
  "sectors_expertise": ["agriculture", "food_processing"],
  "website": "https://nairobidist.com",
  "phone": "+254 20 1234567",
  "is_public": true,
  "availability_status": "available"
}
```

### Expo Virtuale

#### GET /expo/pages/{pmi_id}
Ottiene la pagina Expo Virtuale di una PMI.

**Response**:
```json
{
  "id": 1,
  "pmi_id": 1,
  "title": "Italian Agritech - Innovazione Agricola",
  "subtitle": "Soluzioni tecnologiche per l'agricoltura moderna",
  "description": "Descrizione completa dell'azienda...",
  "logo_url": "/uploads/logos/logo1.png",
  "banner_url": "/uploads/banners/banner1.jpg",
  "video_url": "https://youtube.com/watch?v=...",
  "theme_color": "#0066CC",
  "is_published": true,
  "views_count": 1234,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-02-20T15:45:00Z"
}
```

#### PUT /expo/pages/{pmi_id}
Aggiorna la pagina Expo Virtuale.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "title": "Nuovo titolo",
  "description": "Nuova descrizione",
  "is_published": true
}
```

#### GET /expo/products
Lista i prodotti di una PMI.

**Query Parameters**:
- `pmi_id` (required): ID della PMI
- `category` (optional): Filtra per categoria
- `is_featured` (optional): Solo prodotti in evidenza

**Response**:
```json
{
  "total": 25,
  "items": [
    {
      "id": 1,
      "pmi_id": 1,
      "name": "Trattore Compatto XZ-100",
      "description": "Trattore ideale per piccole aziende agricole",
      "category": "machinery",
      "main_image_url": "/uploads/products/tractor1.jpg",
      "price": 15000,
      "currency": "EUR",
      "is_featured": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### POST /expo/products
Crea un nuovo prodotto.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "name": "Nuovo Prodotto",
  "description": "Descrizione del prodotto",
  "category": "machinery",
  "price": 10000,
  "currency": "EUR",
  "specifications": {"power": "100HP", "weight": "2000kg"}
}
```

### Business Matching

#### GET /matching/suggestions
Ottiene suggerimenti di match per la PMI corrente.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `limit` (optional, default: 10): Numero massimo di risultati

**Response**:
```json
{
  "total": 15,
  "matches": [
    {
      "partner_id": 101,
      "partner_name": "Nairobi Agro Distribution",
      "match_score": 87.5,
      "explanation": "Il partner ha esperienza nel settore agritech. Il partner opera in Kenya, uno dei vostri mercati target.",
      "breakdown": {
        "sector_score": 100,
        "country_score": 100,
        "service_score": 80,
        "size_score": 70,
        "keyword_score": 65,
        "total_score": 87.5
      },
      "partner_data": {
        "country": "Kenya",
        "city": "Nairobi",
        "services_offered": ["distributor", "logistics"]
      }
    }
  ]
}
```

#### POST /matching/accept/{match_id}
Accetta un match suggerito.

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "id": 1,
  "pmi_id": 1,
  "partner_id": 101,
  "status": "accepted",
  "match_score": 87.5
}
```

#### GET /matching/my-matches
Ottiene tutti i match dell'utente corrente.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `status` (optional): Filtra per stato (suggested, accepted, rejected, etc.)

**Response**: Lista di match con dettagli

### Meetings

#### GET /meetings
Lista gli incontri dell'utente corrente.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `status` (optional): Filtra per stato (scheduled, completed, cancelled)
- `from_date` (optional): Data inizio
- `to_date` (optional): Data fine

**Response**:
```json
{
  "total": 5,
  "items": [
    {
      "id": 1,
      "pmi_id": 1,
      "partner_id": 101,
      "title": "Incontro Iniziale - Discussione Partnership",
      "description": "Primo incontro per discutere opportunità di collaborazione",
      "scheduled_at": "2024-03-15T14:00:00Z",
      "duration_minutes": 60,
      "meeting_url": "https://zoom.us/j/123456789",
      "meeting_platform": "zoom",
      "status": "scheduled"
    }
  ]
}
```

#### POST /meetings
Crea un nuovo incontro.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "partner_id": 101,
  "title": "Incontro Iniziale",
  "description": "Discussione partnership",
  "scheduled_at": "2024-03-15T14:00:00Z",
  "duration_minutes": 60,
  "meeting_platform": "zoom"
}
```

### Market Intelligence

#### GET /market/reports
Lista i report di mercato disponibili.

**Query Parameters**:
- `country` (optional): Filtra per paese
- `sector` (optional): Filtra per settore
- `report_type` (optional): Tipo di report

**Response**:
```json
{
  "total": 45,
  "items": [
    {
      "id": 1,
      "title": "Analisi Mercato Agritech Kenya 2024",
      "description": "Report completo sul mercato agritech in Kenya",
      "summary": "Il mercato agritech in Kenya sta crescendo...",
      "country": "Kenya",
      "sector": "agritech",
      "report_type": "market_analysis",
      "cover_image_url": "/uploads/reports/cover1.jpg",
      "file_url": "/uploads/reports/report1.pdf",
      "author": "ICE Kenya",
      "publication_date": "2024-01-10T00:00:00Z",
      "is_premium": false,
      "views_count": 523
    }
  ]
}
```

#### GET /market/news
Lista le notizie dai mercati target.

**Query Parameters**:
- `country` (optional): Filtra per paese
- `category` (optional): Categoria notizia
- `limit` (optional, default: 20): Numero di risultati

**Response**:
```json
{
  "total": 150,
  "items": [
    {
      "id": 1,
      "title": "Kenya lancia nuovo programma per investimenti esteri",
      "summary": "Il governo keniano ha annunciato...",
      "url": "https://source.com/article",
      "image_url": "/uploads/news/news1.jpg",
      "country": "Kenya",
      "category": "economy",
      "source": "Business Daily Africa",
      "published_at": "2024-02-20T10:00:00Z"
    }
  ]
}
```

#### POST /market/alerts
Crea un alert personalizzato.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "name": "Alert Bandi Kenya",
  "keywords": ["tender", "agriculture", "machinery"],
  "countries": ["Kenya"],
  "sectors": ["agritech"],
  "alert_types": ["news", "tenders"],
  "email_notification": true,
  "frequency": "immediate"
}
```

### Training

#### GET /training/events
Lista gli eventi formativi.

**Query Parameters**:
- `event_type` (optional): Tipo evento (webinar, course, workshop)
- `status` (optional): Stato (published, live, completed)
- `upcoming` (optional, boolean): Solo eventi futuri

**Response**:
```json
{
  "total": 12,
  "items": [
    {
      "id": 1,
      "title": "Come Entrare nel Mercato Keniano",
      "description": "Webinar introduttivo sulle opportunità in Kenya",
      "event_type": "webinar",
      "status": "published",
      "cover_image_url": "/uploads/events/event1.jpg",
      "scheduled_at": "2024-03-20T15:00:00Z",
      "duration_minutes": 90,
      "max_participants": 100,
      "registrations_count": 45,
      "issues_certificate": true
    }
  ]
}
```

#### POST /training/events/{event_id}/register
Registra l'utente a un evento.

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "id": 1,
  "event_id": 1,
  "user_id": 1,
  "status": "registered",
  "created_at": "2024-02-20T10:00:00Z"
}
```

## Error Responses

Tutte le API possono restituire i seguenti errori:

### 400 Bad Request
```json
{
  "detail": "Descrizione dell'errore"
}
```

### 401 Unauthorized
```json
{
  "detail": "Token non valido o scaduto"
}
```

### 403 Forbidden
```json
{
  "detail": "Accesso negato. Ruolo richiesto: pmi"
}
```

### 404 Not Found
```json
{
  "detail": "Risorsa non trovata"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Errore interno del server"
}
```

## Rate Limiting

Le API sono soggette a rate limiting:

- **Autenticazione**: 5 richieste/minuto per IP
- **API Generiche**: 100 richieste/minuto per utente
- **Upload File**: 10 richieste/minuto per utente

Headers di risposta:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1614556800
```

## Pagination

Le liste supportano la paginazione:

**Query Parameters**:
- `page` (default: 1): Numero pagina
- `page_size` (default: 20, max: 100): Elementi per pagina

**Response**:
```json
{
  "total": 150,
  "page": 1,
  "page_size": 20,
  "pages": 8,
  "items": [...]
}
```

## File Upload

Per caricare file (immagini, documenti):

**Endpoint**: `POST /upload`

**Headers**: 
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Form Data**:
- `file`: File da caricare
- `type`: Tipo file (logo, product_image, document, etc.)

**Response**:
```json
{
  "url": "/uploads/products/image123.jpg",
  "filename": "image123.jpg",
  "size": 245678,
  "mime_type": "image/jpeg"
}
```

## Webhooks

La piattaforma supporta webhooks per eventi importanti:

- `match.created`: Nuovo match creato
- `meeting.scheduled`: Incontro programmato
- `meeting.completed`: Incontro completato
- `alert.triggered`: Alert attivato

Configurazione webhooks disponibile nel profilo amministratore.

## SDK e Librerie

### JavaScript/TypeScript
```bash
npm install @abb/api-client
```

### Python
```bash
pip install abb-api-client
```

## Support

Per supporto tecnico: api-support@africabusinessbridge.com

Documentazione interattiva: https://api.africabusinessbridge.com/docs

