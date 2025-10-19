# Africa Business Bridge

**Piattaforma digitale per connettere le PMI italiane con opportunità di business in Kenya, Tanzania ed Etiopia**

## 📋 Panoramica

Africa Business Bridge è una piattaforma web completa che serve come hub digitale per facilitare le connessioni commerciali tra le piccole e medie imprese italiane e i mercati africani emergenti. La piattaforma integra servizi commerciali, market intelligence, business matching basato su IA, formazione e ora anche **contratti digitali in blockchain e un sistema di pagamenti integrato**.

## 🎯 Caratteristiche Principali

### Per le PMI Italiane
- **Expo Virtuale**: Vetrina digitale personalizzabile per prodotti e servizi
- **Business Matching con IA**: Algoritmo intelligente per trovare partner locali compatibili
- **Market Intelligence**: Report, analisi di mercato e notizie aggiornate
- **Formazione**: Webinar, corsi e workshop per l'internazionalizzazione
- **Calendario B2B**: Gestione incontri e videocall con partner
- **Contratti Blockchain**: Gestione di accordi digitali sicuri e trasparenti tramite smart contract
- **Sistema di Pagamenti Integrato**: Conversione e trasferimento di fondi (fiat-to-crypto, crypto-to-fiat) per pagamenti contrattuali

### Per i Partner Locali
- **Profilo Pubblico**: Visibilità verso le PMI italiane
- **Gestione Servizi**: Presentazione dei servizi offerti
- **Sistema di Messaggistica**: Comunicazione diretta con le PMI
- **Calendario**: Gestione disponibilità e incontri
- **Contratti Blockchain**: Partecipazione ad accordi digitali e gestione delle milestone
- **Sistema di Pagamenti Integrato**: Ricezione di pagamenti sicuri tramite stablecoin

### Per gli Amministratori
- **Dashboard Completa**: Gestione utenti e contenuti
- **Statistiche**: Analytics e report di utilizzo
- **Gestione Contenuti**: Pubblicazione report e notizie
- **Sistema di Notifiche**: Alert e comunicazioni agli utenti
- **Monitoraggio Contratti Blockchain**: Supervisione degli accordi e delle transazioni
- **Gestione Pagamenti**: Monitoraggio delle operazioni di on-ramp e off-ramp

## 🏗️ Architettura Tecnica

### Frontend
- **Framework**: React con Next.js
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Routing**: React Router
- **State Management**: Context API

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Autenticazione**: JWT (JSON Web Tokens)
- **API Documentation**: OpenAPI/Swagger
- **Blockchain Integration**: web3.py per interazione con Polygon
- **Payment Gateways**: Integrazione con Circle, Transak, MoonPay (via API)

### Infrastruttura
- **Architettura**: Microservizi
- **Cache**: Redis
- **Task Queue**: Celery
- **File Storage**: Sistema locale (estendibile a S3)
- **Blockchain**: Polygon (per smart contract e transazioni)

## 📁 Struttura del Progetto

```
africa-business-bridge/
├── frontend/                 # Applicazione React
│   ├── src/
│   │   ├── components/      # Componenti riutilizzabili
│   │   ├── contexts/        # Context API (Auth, etc.)
│   │   ├── pages/           # Pagine dell'applicazione
│   │   ├── hooks/           # Custom React hooks
│   │   └── lib/             # Utility functions
│   └── public/              # Asset statici
│
├── api/                      # API FastAPI (Ristrutturata per Vercel)
│   ├── app/
│   │   ├── api/            # Route API (incluse blockchain e payments)
│   │   ├── core/           # Configurazione e security
│   │   ├── models/         # Modelli SQLAlchemy
│   │   ├── schemas/        # Schemi Pydantic (incluse blockchain e payments)
│   │   ├── services/       # Business logic (inclusi blockchain e payments)
│   │   └── utils/          # Utility functions
│   └── tests/              # Test unitari e integrazione
│
├── blockchain/               # Smart Contracts Solidity
│   ├── contracts/          # File .sol degli smart contract
│   └── scripts/            # Script per deployment e interazione (opzionale)
│
├── database/               # Script di migrazione
├── ai_models/              # Algoritmi di matching
└── docs/                   # Documentazione
```

## 🚀 Installazione e Setup

### Prerequisiti
- Node.js 18+ e pnpm
- Python 3.11+
- PostgreSQL 14+
- Redis (opzionale, per cache e task queue)
- Wallet Ethereum/Polygon (es. MetaMask) configurato per Polygon Mumbai Testnet (per sviluppo blockchain)

### Setup Backend

1. Naviga nella directory `api`:
```bash
cd api
```

2. Crea un ambiente virtuale Python:
```bash
python3.11 -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

3. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

4. Configura le variabili d'ambiente:
```bash
cp .env.example .env
# Modifica .env con le tue configurazioni (incluse le chiavi API per i servizi di pagamento e le credenziali blockchain)
```

5. Crea il database PostgreSQL:
```bash
createdb africa_business_bridge
```

6. Avvia il server:
```bash
python -m app.main
# oppure
uvicorn app.main:app --reload
```

L'API sarà disponibile su `http://localhost:8000`
La documentazione Swagger su `http://localhost:8000/api/docs`

### Setup Frontend

1. Naviga nella directory `frontend`:
```bash
cd frontend
```

2. Installa le dipendenze:
```bash
pnpm install
```

3. Configura le variabili d'ambiente:
```bash
# Il file .env è già configurato con:
VITE_API_URL=http://localhost:8000/api/v1
```

4. Avvia il server di sviluppo:
```bash
pnpm run dev
```

L'applicazione sarà disponibile su `http://localhost:5173`

## 📊 Modelli del Database

### Utenti e Profili
- **User**: Utente base con credenziali
- **PMIProfile**: Profilo azienda PMI italiana
- **PartnerProfile**: Profilo partner locale
- **AdminProfile**: Profilo amministratore

### Expo Virtuale
- **ExpoPage**: Pagina vetrina dell'azienda
- **Product**: Prodotti nel catalogo
- **MediaItem**: Gallery immagini e video
- **Document**: Documenti e brochure

### Business Matching
- **BusinessMatch**: Match tra PMI e partner
- **Meeting**: Incontri B2B programmati
- **Message**: Messaggi tra utenti

### Market Intelligence
- **MarketReport**: Report e analisi di mercato
- **NewsItem**: Notizie dai mercati target
- **Alert**: Alert personalizzati per utenti

### Formazione
- **TrainingEvent**: Eventi formativi (webinar, workshop)
- **EventRegistration**: Registrazioni agli eventi
- **Course**: Corsi strutturati
- **Lesson**: Lezioni dei corsi
- **CourseEnrollment**: Iscrizioni ai corsi

### Blockchain & Pagamenti
- **BlockchainContract**: Riferimento ai contratti on-chain (per tracciamento)
- **PaymentTransaction**: Record delle transazioni di pagamento (on-ramp/off-ramp)
- **Wallet**: Indirizzi wallet degli utenti

## 🔐 Autenticazione

Il sistema utilizza JWT (JSON Web Tokens) per l'autenticazione:

- **Access Token**: Valido per 30 minuti
- **Refresh Token**: Valido per 7 giorni

### Endpoint di Autenticazione

- `POST /api/v1/auth/register` - Registrazione nuovo utente
- `POST /api/v1/auth/login` - Login e ottenimento token
- `POST /api/v1/auth/refresh` - Rinnovo token
- `GET /api/v1/auth/me` - Informazioni utente corrente
- `POST /api/v1/auth/change-password` - Cambio password
- `POST /api/v1/auth/logout` - Logout

## 🎨 Design System

### Colori
- **Primario (Blu Italia)**: `oklch(0.45 0.15 250)`
- **Secondario (Arancione Africa)**: `oklch(0.70 0.18 50)`
- **Background**: Toni chiari e neutri
- **Accenti**: Verde per successo, rosso per errori

### Tipografia
- Font system native per performance ottimali
- Gerarchia chiara con dimensioni responsive

### Componenti UI
- Utilizzo di shadcn/ui per componenti consistenti
- Animazioni fluide con Tailwind CSS
- Design responsive mobile-first

## 🔄 Prossimi Sviluppi

### Fase 1 - Completata ✅
- [x] Struttura progetto
- [x] Modelli database
- [x] Sistema autenticazione
- [x] Dashboard base

### Fase 2 - Completata ✅
- [x] Modulo Expo Virtuale completo
- [x] Sistema upload file
- [x] Catalogo prodotti

### Fase 3 - Completata ✅
- [x] Algoritmo Business Matching con IA
- [x] Integrazione API videocall (Zoom/Google Meet)
- [x] Sistema di messaggistica real-time

### Fase 4 - Completata ✅
- [x] Scraper per Market Intelligence
- [x] Sistema alert personalizzati
- [x] Feed notizie automatizzato

### Fase 5 - Completata ✅
- [x] Piattaforma formazione completa
- [x] Sistema certificati PDF
- [x] Gestione webinar live

### Nuove Funzionalità (Implementate) ✅
- [x] **Contratti Blockchain**: Implementazione smart contract e API per gestione accordi
- [x] **Sistema di Pagamenti Integrato**: Implementazione servizi e API per on-ramp/off-ramp (fiat-to-crypto, crypto-to-fiat)

## 📝 API Documentation

La documentazione completa delle API è disponibile tramite Swagger UI una volta avviato il backend:

- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`
- **OpenAPI JSON**: `http://localhost:8000/api/openapi.json`

## 🧪 Testing

### Backend
```bash
cd api
pytest
```

### Frontend
```bash
cd frontend
pnpm test
```

## 🤝 Contribuire

Questo è un progetto in sviluppo. Per contribuire:

1. Crea un branch per la tua feature
2. Implementa le modifiche con test
3. Assicurati che tutti i test passino
4. Crea una pull request con descrizione dettagliata

## 📄 Licenza

Questo progetto è proprietario e riservato.

## 👥 Team

Sviluppato per Italian Business Partners (IBP)

## 📞 Contatti

Per informazioni sul progetto, contattare il team di sviluppo.

---

**Versione**: 1.1.0  
**Ultimo aggiornamento**: 2025

