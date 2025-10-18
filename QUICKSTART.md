# Quick Start Guide - Africa Business Bridge

Guida rapida per avviare e testare la piattaforma Africa Business Bridge in ambiente di sviluppo.

## 🚀 Avvio Rapido

### Prerequisiti Verificati
- ✅ Node.js 22.13.0
- ✅ Python 3.11
- ✅ pnpm installato
- ⚠️ PostgreSQL (da installare)
- ⚠️ Redis (opzionale)

## Passo 1: Setup Database PostgreSQL

### Opzione A: Installazione Locale (Consigliata per Produzione)

```bash
# Installa PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Avvia PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Crea database e utente
sudo -u postgres psql << EOF
CREATE DATABASE africa_business_bridge;
CREATE USER abb_user WITH PASSWORD 'dev_password_123';
GRANT ALL PRIVILEGES ON DATABASE africa_business_bridge TO abb_user;
\q
EOF
```

### Opzione B: SQLite per Test Rapidi

Per test rapidi senza PostgreSQL, modifica il backend per usare SQLite:

```python
# In backend/app/core/config.py, cambia:
DATABASE_URL: str = "sqlite:///./africa_business_bridge.db"
```

## Passo 2: Avvio Backend

```bash
# Naviga nella directory backend
cd /home/ubuntu/africa-business-bridge/backend

# Crea ambiente virtuale
python3.11 -m venv venv
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Crea file .env
cat > .env << 'EOF'
DATABASE_URL=postgresql://abb_user:dev_password_123@localhost:5432/africa_business_bridge
SECRET_KEY=dev-secret-key-change-in-production-12345678901234567890
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
EOF

# Avvia il server
python -m app.main
```

Il backend sarà disponibile su:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Passo 3: Avvio Frontend

Apri un nuovo terminale:

```bash
# Naviga nella directory frontend
cd /home/ubuntu/africa-business-bridge/frontend

# Le dipendenze sono già installate
# Se necessario: pnpm install

# Verifica file .env
cat .env
# Dovrebbe contenere: VITE_API_URL=http://localhost:8000/api/v1

# Avvia il server di sviluppo
pnpm run dev --host
```

Il frontend sarà disponibile su:
- **App**: http://localhost:5173

## Passo 4: Test dell'Applicazione

### 1. Registrazione Utente

1. Apri il browser su http://localhost:5173
2. Clicca su "Registrati"
3. Compila il form:
   - Nome completo: Mario Rossi
   - Email: mario.rossi@example.com
   - Tipo profilo: Azienda PMI Italiana
   - Password: TestPass123
   - Conferma password: TestPass123
4. Clicca "Registrati"

### 2. Login

1. Dopo la registrazione, verrai reindirizzato al login
2. Inserisci le credenziali:
   - Email: mario.rossi@example.com
   - Password: TestPass123
3. Clicca "Accedi"

### 3. Dashboard

Dopo il login, vedrai la dashboard con:
- Statistiche (dati di esempio)
- Menu laterale con tutte le sezioni
- Azioni rapide
- Attività recenti

### 4. Test API con Swagger

1. Apri http://localhost:8000/api/docs
2. Prova gli endpoint:
   - POST /api/v1/auth/register
   - POST /api/v1/auth/login
   - GET /api/v1/auth/me (richiede token)

## 📊 Struttura Progetto Creata

```
africa-business-bridge/
├── frontend/                    ✅ Completato
│   ├── src/
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx  # Gestione autenticazione
│   │   ├── pages/
│   │   │   ├── Login.jsx        # Pagina login
│   │   │   ├── Register.jsx     # Pagina registrazione
│   │   │   └── Dashboard.jsx    # Dashboard principale
│   │   ├── App.jsx              # Router principale
│   │   └── App.css              # Stili personalizzati
│   └── .env                     # Configurazione
│
├── backend/                     ✅ Completato
│   ├── app/
│   │   ├── api/
│   │   │   └── auth.py          # API autenticazione
│   │   ├── core/
│   │   │   ├── config.py        # Configurazione
│   │   │   ├── database.py      # Setup database
│   │   │   ├── security.py      # JWT e password
│   │   │   └── dependencies.py  # Dependencies FastAPI
│   │   ├── models/
│   │   │   ├── user.py          # Modelli utente
│   │   │   ├── expo.py          # Modelli Expo Virtuale
│   │   │   ├── business.py      # Modelli Business Matching
│   │   │   └── training.py      # Modelli Formazione
│   │   ├── schemas/
│   │   │   └── auth.py          # Schemi Pydantic
│   │   └── main.py              # App FastAPI
│   ├── requirements.txt         # Dipendenze Python
│   └── .env                     # Configurazione
│
├── ai_models/                   ✅ Completato
│   └── matching_algorithm.py    # Algoritmo matching IA
│
├── docs/                        ✅ Completato
│   ├── API_DOCUMENTATION.md     # Documentazione API
│   └── DEPLOYMENT.md            # Guida deployment
│
├── README.md                    ✅ Completato
└── QUICKSTART.md               ✅ Questo file
```

## 🎯 Funzionalità Implementate

### ✅ Fase 1-3: Base e Autenticazione
- [x] Struttura progetto completa
- [x] Modelli database per tutti i moduli
- [x] Sistema autenticazione JWT
- [x] API di registrazione e login
- [x] Frontend React con routing
- [x] Pagine Login e Register
- [x] Dashboard con sidebar dinamica
- [x] Context API per gestione stato
- [x] Design system personalizzato (colori Italia/Africa)

### 📋 Prossime Fasi da Implementare

#### Fase 4: Modulo Expo Virtuale
- [ ] API per gestione Expo Page
- [ ] API per gestione Prodotti
- [ ] Upload immagini e documenti
- [ ] Pagina Expo nel frontend
- [ ] Editor prodotti

#### Fase 5: Business Matching
- [ ] Integrazione algoritmo IA
- [ ] API per matching
- [ ] Pagina Partner nel frontend
- [ ] Sistema di messaggistica

#### Fase 6: Market Intelligence
- [ ] Scraper per notizie
- [ ] API per report e news
- [ ] Sistema alert
- [ ] Pagina Market Intelligence

#### Fase 7: Formazione
- [ ] API per eventi e corsi
- [ ] Sistema registrazioni
- [ ] Generazione certificati PDF
- [ ] Pagina Formazione

## 🔧 Comandi Utili

### Backend

```bash
# Attiva ambiente virtuale
cd backend
source venv/bin/activate

# Avvia server
python -m app.main

# Avvia con reload automatico
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test (quando implementati)
pytest

# Crea migrazione database (con Alembic)
alembic revision --autogenerate -m "descrizione"
alembic upgrade head
```

### Frontend

```bash
cd frontend

# Installa dipendenze
pnpm install

# Avvia dev server
pnpm run dev

# Build produzione
pnpm run build

# Preview build
pnpm run preview

# Lint
pnpm run lint
```

## 🐛 Troubleshooting

### Backend non si avvia

**Errore: "ModuleNotFoundError"**
```bash
# Verifica ambiente virtuale attivo
which python  # Dovrebbe mostrare path con 'venv'

# Reinstalla dipendenze
pip install -r requirements.txt
```

**Errore: "Database connection failed"**
```bash
# Verifica PostgreSQL in esecuzione
sudo systemctl status postgresql

# Verifica credenziali in .env
cat backend/.env | grep DATABASE_URL

# Test connessione manuale
psql -U abb_user -d africa_business_bridge -h localhost
```

### Frontend non si avvia

**Errore: "ECONNREFUSED"**
```bash
# Verifica che il backend sia in esecuzione
curl http://localhost:8000/health

# Verifica VITE_API_URL in .env
cat frontend/.env
```

**Errore: "Module not found"**
```bash
# Reinstalla dipendenze
rm -rf node_modules
pnpm install
```

### CORS Errors

Se vedi errori CORS nel browser:

1. Verifica che il frontend URL sia in `BACKEND_CORS_ORIGINS` nel backend/.env
2. Riavvia il backend dopo aver modificato .env

## 📚 Documentazione Aggiuntiva

- **API Documentation**: Vedi `docs/API_DOCUMENTATION.md`
- **Deployment Guide**: Vedi `docs/DEPLOYMENT.md`
- **README Principale**: Vedi `README.md`

## 🧪 Test con dati di esempio

### Crea utenti di test

```bash
# Avvia Python nel backend
cd backend
source venv/bin/activate
python

# In Python:
from app.core.database import SessionLocal
from app.models.user import User, UserRole, PMIProfile, PartnerProfile
from app.core.security import get_password_hash

db = SessionLocal()

# Crea PMI
pmi_user = User(
    email="pmi@test.com",
    full_name="Test PMI",
    role=UserRole.PMI,
    hashed_password=get_password_hash("TestPass123"),
    is_active=True
)
db.add(pmi_user)
db.commit()

# Crea Partner
partner_user = User(
    email="partner@test.com",
    full_name="Test Partner",
    role=UserRole.PARTNER,
    hashed_password=get_password_hash("TestPass123"),
    is_active=True
)
db.add(partner_user)
db.commit()

# Crea Admin
admin_user = User(
    email="admin@test.com",
    full_name="Test Admin",
    role=UserRole.ADMIN,
    hashed_password=get_password_hash("TestPass123"),
    is_active=True
)
db.add(admin_user)
db.commit()

print("Utenti di test creati!")
db.close()
```

### Credenziali di test

- **PMI**: pmi@test.com / TestPass123
- **Partner**: partner@test.com / TestPass123
- **Admin**: admin@test.com / TestPass123

## 🎨 Personalizzazione

### Cambiare i colori

Modifica `frontend/src/App.css`:

```css
:root {
  /* Colore primario (blu) */
  --primary: oklch(0.45 0.15 250);
  
  /* Colore secondario (arancione) */
  --secondary: oklch(0.70 0.18 50);
}
```

### Aggiungere nuove route

1. Crea componente in `frontend/src/pages/`
2. Aggiungi route in `frontend/src/App.jsx`
3. Aggiungi voce menu in `frontend/src/pages/Dashboard.jsx`

## 📞 Supporto

Per problemi o domande:
1. Controlla la sezione Troubleshooting
2. Verifica i log del backend e frontend
3. Consulta la documentazione API

## 🚀 Prossimi Passi

1. **Testa l'autenticazione**: Registrati e fai login
2. **Esplora la dashboard**: Naviga tra le diverse sezioni
3. **Testa le API**: Usa Swagger per testare gli endpoint
4. **Inizia lo sviluppo**: Implementa i moduli rimanenti

---

**Buon sviluppo! 🎉**

