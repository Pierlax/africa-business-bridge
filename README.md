# Africa Business Bridge

**Piattaforma digitale per connettere le PMI italiane con opportunità di business in Kenya, Tanzania ed Etiopia**

## 📋 Panoramica

Africa Business Bridge è una piattaforma web completa che serve come hub digitale per facilitare le connessioni commerciali tra le piccole e medie imprese italiane e i mercati africani emergenti. La piattaforma integra servizi commerciali, market intelligence, business matching basato su IA, formazione, **contratti digitali in blockchain, un sistema di pagamenti integrato**, **gestione avanzata di ordini, logistica, ispezioni e verifica KYC/KYB**, e ora anche **funzionalità avanzate per l'adozione utente, Onboarding Guidato, Rivelazione Progressiva, UX Writing e Analytics**, e un **sistema di alert** per la gestione delle notifiche.

## 🎯 Caratteristiche Principali

### Per le PMI Italiane
- **Expo Virtuale**: Vetrina digitale personalizzabile per prodotti e servizi
- **Business Matching con IA**: Algoritmo intelligente per trovare partner locali compatibili
- **Market Intelligence**: Report, analisi di mercato e notizie aggiornate
- **Formazione**: Webinar, corsi e workshop per l'internazionalizzazione
- **Calendario B2B**: Gestione incontri e videocall con partner
- **Contratti Blockchain**: Gestione di accordi digitali sicuri e trasparenti tramite smart contract
- **Sistema di Pagamenti Integrato**: Conversione e trasferimento di fondi (fiat-to-crypto, crypto-to-fiat) per pagamenti contrattuali
- **Gestione Ordini (OMS)**: Creazione, tracciamento e gestione di ordini B2B con milestone e pagamenti automatici
- **Gestione Logistica**: Richiesta quotazioni, tracciamento spedizioni e integrazione con provider
- **Ispezioni**: Richiesta e gestione di servizi di ispezione per le merci
- **Verifica KYC/KYB**: Processo di verifica avanzato per garantire la fiducia tra le parti
- **Onboarding Guidato**: Percorsi personalizzati per i nuovi utenti per massimizzare l'adozione
- **Rivelazione Progressiva**: Funzionalità avanzate svelate al momento giusto, basandosi sull'interazione dell'utente

### Per i Partner Locali
- **Profilo Pubblico**: Visibilità verso le PMI italiane
- **Gestione Servizi**: Presentazione dei servizi offerti
- **Sistema di Messaggistica**: Comunicazione diretta con le PMI
- **Calendario**: Gestione disponibilità e incontri
- **Contratti Blockchain**: Partecipazione ad accordi digitali e gestione delle milestone
- **Sistema di Pagamenti Integrato**: Ricezione di pagamenti sicuri tramite stablecoin
- **Gestione Ordini (OMS)**: Accettazione e gestione degli ordini ricevuti
- **Gestione Logistica**: Gestione delle spedizioni e interazione con i provider
- **Ispezioni**: Gestione delle ispezioni richieste per le merci
- **Verifica KYC/KYB**: Processo di verifica avanzato per garantire la fiducia tra le parti

### Per gli Amministratori
- **Dashboard Completa**: Gestione utenti e contenuti
- **Statistiche**: Analytics e report di utilizzo
- **Gestione Contenuti**: Pubblicazione report e notizie
- **Sistema di Notifiche**: Alert e comunicazioni agli utenti
- **Monitoraggio Contratti Blockchain**: Supervisione degli accordi e delle transazioni
- **Gestione Pagamenti**: Monitoraggio delle operazioni di on-ramp e off-ramp
- **Gestione Verifiche KYC/KYB**: Revisione e approvazione delle richieste di verifica
- **Monitoraggio Ordini, Logistica e Ispezioni**: Supervisione completa delle operazioni commerciali
- **Dashboard Analytics**: Monitoraggio delle metriche di adozione utente, funnel di conversione e punti di abbandono
- **Sistema di Alert**: Notifiche automatiche su anomalie o metriche critiche

## 🏗️ Architettura Tecnica

### Frontend
- **Framework**: React con Vite
- **Ottimizzazioni Frontend**: Lazy loading, code splitting, image optimization (tramite `vite.config.js` e `lazyLoad.jsx`)
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Routing**: React Router
- **State Management**: Context API
- **Data Visualization**: Recharts (per Analytics Dashboard)

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Autenticazione**: JWT (JSON Web Tokens)
- **API Documentation**: OpenAPI/Swagger
- **Blockchain Integration**: web3.py per interazione con Polygon
- **Payment Gateways**: Integrazione con Circle, Transak, MoonPay (via API)
- **Analytics**: Tracciamento azioni utente, funnel di conversione, alert

### Infrastruttura
- **Architettura**: Microservizi
- **Cache**: Redis (per caching backend e broker Celery)
- **Task Queue**: Celery (per task asincroni come generazione PDF, matching AI)
- **File Storage**: Sistema locale (estendibile a S3)
- **Blockchain**: Polygon (per smart contract e transazioni)

## 📁 Struttura del Progetto

```
africa-business-bridge/
├── frontend/                 # Applicazione React
│   ├── src/
│   │   ├── components/      # Componenti riutilizzabili (incluse OnboardingDashboard, ProgressiveDisclosure, LanguageSwitcher)
│   │   ├── contexts/        # Context API (Auth, etc.)
│   │   ├── i18n/            # Configurazione e traduzioni per multi-lingua
│   │   ├── pages/           # Pagine dell\'applicazione (incluse AnalyticsDashboard)
│   │   ├── hooks/           # Custom React hooks
│   │   ├── utils/           # Utility functions (incluso uxWriting.js, lazyLoad.jsx)
│   │   └── lib/             # Utility functions
│   └── public/              # Asset statici
│
├── api/                      # API FastAPI
│   ├── app/
│   │   ├── api/            # Route API (incluse blockchain, payments, verification, orders, logistics, analytics)
│   │   ├── core/           # Configurazione, security, redis_cache.py, celery_app.py
│   │   ├── tasks/          # Task Celery (certificates, matching, market_intelligence, maintenance)
│   │   ├── models/         # Modelli SQLAlchemy (incluse verification, orders, logistics, analytics)
│   │   ├── schemas/        # Schemi Pydantic (incluse blockchain, payments, verification, orders, logistics, analytics)
│   │   ├── services/       # Business logic (inclusi blockchain, payments, verification, orders, logistics, analytics)
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

### Moduli Avanzati (Distichain-inspired)
- **Verifica (KYC/KYB)**: Gestione delle richieste di verifica per utenti e aziende.
- **Ordini (OMS)**: Creazione, gestione e tracciamento degli ordini B2B.
- **Logistica**: Gestione delle spedizioni, quotazioni e tracciamento.
- **Ispezione**: Richiesta e gestione dei servizi di ispezione.

### Adozione Utente & Analytics
- **UserAction**: Tracciamento delle azioni chiave degli utenti per l'onboarding e l'adozione.
- **ConversionMetric**: Metriche aggregate sul funnel di conversione.
- **Alert**: Notifiche automatiche su anomalie o metriche critiche.

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

## 🚀 Miglioramenti Implementati

Questa sezione riassume i miglioramenti implementati a seguito dell'analisi della piattaforma.

### 1. Performance e Scalabilità
- **Ottimizzazione Frontend**: Configurazione di `vite.config.js` per code splitting e minificazione. Introduzione di `lazyLoad.jsx` per lazy loading di componenti e ottimizzazione delle immagini. (Vedi `frontend/vite.config.js`, `frontend/src/utils/lazyLoad.jsx`)
- **Strategia di Caching Backend**: Implementazione di un modulo `redis_cache.py` per il caching delle risposte API e dei dati frequenti utilizzando Redis. (Vedi `api/app/core/redis_cache.py`)
- **Elaborazione Task Asincroni**: Integrazione di Celery per la gestione asincrona di task a lunga esecuzione, come la generazione di certificati PDF e i calcoli di matching AI. Creazione di moduli `certificates.py` e `matching.py` in `api/app/tasks/`. (Vedi `api/app/core/celery_app.py`, `api/app/tasks/certificates.py`, `api/app/tasks/matching.py`)

### 2. User Experience e Funzionalità
- **Supporto Multi-lingua**: Implementazione di una struttura i18n nel frontend con file di traduzione per Italiano, Inglese, Swahili e Amarico, e un componente `LanguageSwitcher`. (Vedi `frontend/src/i18n/config.js`, `frontend/src/i18n/locales/`, `frontend/src/components/LanguageSwitcher.jsx`)

### 3. Sicurezza e Conformità
- **Documentazione Sicurezza e Compliance**: Creazione di un documento `SECURITY_COMPLIANCE.md` che delinea le linee guida per audit di sicurezza, conformità GDPR e audit di smart contract. (Vedi `docs/SECURITY_COMPLIANCE.md`)

### 4. DevOps e Monitoraggio
- **Documentazione DevOps e Monitoraggio**: Creazione di un documento `DEVOPS_MONITORING.md` che fornisce una guida completa per l'implementazione di pipeline CI/CD con GitHub Actions, strategie di testing, logging centralizzato (ELK Stack), monitoraggio (Prometheus/Grafana) e IaC con Terraform. (Vedi `docs/DEVOPS_MONITORING.md`)

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
- [x] **Modulo di Verifica Avanzata (KYC/KYB)**: Implementazione modelli, schemi e API per la gestione delle richieste di verifica.
- [x] **Modulo di Gestione Ordini (OMS)**: Implementazione modelli, schemi e API per la creazione, gestione e tracciamento degli ordini B2B.
- [x] **Modulo di Gestione Logistica**: Implementazione modelli, schemi e API per la gestione delle spedizioni, quotazioni e tracciamento.
- [x] **Modulo di Ispezione**: Implementazione modelli, schemi e API per la richiesta e gestione dei servizi di ispezione.
- [x] **Onboarding Guidato**: Percorsi personalizzati per i nuovi utenti per massimizzare l'adozione.
- [x] **Rivelazione Progressiva**: Funzionalità avanzate svelate al momento giusto, basandosi sull'interazione dell'utente.
- [x] **UX Writing**: Applicazione di linee guida per un linguaggio chiaro, orientato al valore e contestuale.
- [x] **Analytics e Alert**: Dashboard analitica per monitorare metriche chiave e sistema di alert automatici.

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

**Versione**: 1.3.0
**Ultimo aggiornamento**: 2025
