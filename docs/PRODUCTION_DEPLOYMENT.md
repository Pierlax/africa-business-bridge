# Guida al Deployment in Produzione - Africa Business Bridge

## Introduzione

Questa guida fornisce istruzioni dettagliate per deployare la piattaforma Africa Business Bridge in un ambiente di produzione utilizzando **Docker** e **Docker Compose**. Il deployment include backend FastAPI, frontend React, database PostgreSQL e Redis per caching.

## Prerequisiti

Prima di iniziare, assicurati di avere:

- **Server Linux** (Ubuntu 22.04 LTS consigliato) con almeno:
  - 2 CPU cores
  - 4GB RAM
  - 50GB storage
- **Docker** e **Docker Compose** installati
- **Dominio** configurato con DNS (es. `africabusinessbridge.com`)
- **Certificato SSL/TLS** (consigliato Let's Encrypt)
- Accesso **SSH** al server

## 1. Preparazione del Server

### 1.1 Installazione Docker

```bash
# Aggiorna i pacchetti
sudo apt-get update
sudo apt-get upgrade -y

# Installa Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Aggiungi utente al gruppo docker
sudo usermod -aG docker $USER

# Installa Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verifica installazione
docker --version
docker-compose --version
```

### 1.2 Configurazione Firewall

```bash
# Abilita firewall
sudo ufw enable

# Permetti SSH
sudo ufw allow 22/tcp

# Permetti HTTP e HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verifica stato
sudo ufw status
```

## 2. Configurazione dell'Applicazione

### 2.1 Clona il Repository

```bash
# Clona il progetto
git clone https://github.com/your-org/africa-business-bridge.git
cd africa-business-bridge
```

### 2.2 Configurazione Variabili d'Ambiente

```bash
# Copia il file di esempio
cp .env.production.example .env.production

# Modifica con i tuoi valori
nano .env.production
```

**Valori Critici da Modificare**:

```bash
# Genera una chiave segreta sicura
SECRET_KEY=$(openssl rand -hex 32)

# Password database forte
DB_PASSWORD=$(openssl rand -base64 32)

# Domini di produzione
BACKEND_CORS_ORIGINS=https://africabusinessbridge.com
VITE_API_URL=https://api.africabusinessbridge.com/api/v1
```

### 2.3 Configurazione Frontend

```bash
# Crea file .env per il frontend
cat > frontend/.env << EOF
VITE_API_URL=https://api.africabusinessbridge.com/api/v1
EOF
```

## 3. Build e Avvio dei Container

### 3.1 Build delle Immagini

```bash
# Build di tutti i servizi
docker-compose -f docker-compose.yml --env-file .env.production build

# Verifica immagini create
docker images | grep abb
```

### 3.2 Avvio dei Servizi

```bash
# Avvia tutti i servizi in background
docker-compose -f docker-compose.yml --env-file .env.production up -d

# Verifica stato dei container
docker-compose ps

# Visualizza log
docker-compose logs -f
```

### 3.3 Inizializzazione Database

```bash
# Accedi al container backend
docker exec -it abb_backend bash

# Esegui migrazioni (se configurate con Alembic)
alembic upgrade head

# Oppure crea le tabelle direttamente
python -c "from app.core.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine)"

# Esci dal container
exit
```

## 4. Configurazione Reverse Proxy (Nginx)

Per servire l'applicazione su HTTPS con certificato SSL, configura un reverse proxy Nginx sul server host.

### 4.1 Installazione Nginx

```bash
sudo apt-get install nginx -y
```

### 4.2 Configurazione Nginx

```bash
# Crea file di configurazione
sudo nano /etc/nginx/sites-available/africabusinessbridge
```

```nginx
# Frontend
server {
    listen 80;
    server_name africabusinessbridge.com www.africabusinessbridge.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Backend API
server {
    listen 80;
    server_name api.africabusinessbridge.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (se necessario)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Abilita il sito
sudo ln -s /etc/nginx/sites-available/africabusinessbridge /etc/nginx/sites-enabled/

# Testa configurazione
sudo nginx -t

# Riavvia Nginx
sudo systemctl restart nginx
```

### 4.3 Certificato SSL con Let's Encrypt

```bash
# Installa Certbot
sudo apt-get install certbot python3-certbot-nginx -y

# Ottieni certificato SSL
sudo certbot --nginx -d africabusinessbridge.com -d www.africabusinessbridge.com -d api.africabusinessbridge.com

# Verifica auto-renewal
sudo certbot renew --dry-run
```

## 5. Monitoraggio e Manutenzione

### 5.1 Health Checks

```bash
# Verifica stato servizi
curl http://localhost:8000/health
curl http://localhost/health

# Verifica database
docker exec abb_postgres psql -U postgres -d africa_business_bridge -c "SELECT version();"
```

### 5.2 Visualizzazione Log

```bash
# Log di tutti i servizi
docker-compose logs -f

# Log di un servizio specifico
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# Log Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 5.3 Backup Database

```bash
# Crea script di backup
cat > backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/abb"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker exec abb_postgres pg_dump -U postgres africa_business_bridge | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Mantieni solo ultimi 7 giorni
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
EOF

chmod +x backup_db.sh

# Aggiungi a crontab per backup giornaliero
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/backup_db.sh") | crontab -
```

### 5.4 Aggiornamento Applicazione

```bash
# Pull delle ultime modifiche
git pull origin main

# Rebuild e riavvio servizi
docker-compose -f docker-compose.yml --env-file .env.production build
docker-compose -f docker-compose.yml --env-file .env.production up -d

# Verifica deployment
docker-compose ps
```

## 6. Sicurezza

### 6.1 Checklist Sicurezza

- [x] **SECRET_KEY** cambiata con valore sicuro e casuale
- [x] **Database password** forte e unica
- [x] **CORS** configurato solo per domini di produzione
- [x] **HTTPS** abilitato con certificato SSL valido
- [x] **Firewall** configurato per permettere solo porte necessarie
- [x] **Rate Limiting** abilitato
- [x] **Backup automatici** configurati
- [ ] **Monitoring** configurato (Sentry, Prometheus, ecc.)
- [ ] **Log rotation** configurato
- [ ] **Fail2ban** installato per protezione brute-force

### 6.2 Hardening Aggiuntivo

```bash
# Disabilita accesso SSH con password (solo chiavi)
sudo nano /etc/ssh/sshd_config
# Imposta: PasswordAuthentication no
sudo systemctl restart sshd

# Configura fail2ban
sudo apt-get install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Aggiorna regolarmente il sistema
sudo apt-get update && sudo apt-get upgrade -y
```

## 7. Scaling e Performance

### 7.1 Scaling Orizzontale

Per gestire più traffico, considera:

- **Load Balancer**: Nginx o HAProxy davanti a più istanze backend
- **Database Replication**: PostgreSQL con replica master-slave
- **Redis Cluster**: Per caching distribuito
- **CDN**: CloudFlare o AWS CloudFront per asset statici

### 7.2 Ottimizzazioni Database

```sql
-- Crea indici per query frequenti
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_expo_pages_pmi_id ON expo_pages(pmi_id);
CREATE INDEX idx_products_pmi_id ON products(pmi_id);
CREATE INDEX idx_matches_pmi_id ON business_matches(pmi_id);
CREATE INDEX idx_matches_partner_id ON business_matches(partner_id);
CREATE INDEX idx_news_published_at ON news_items(published_at DESC);
```

## 8. Monitoring e Alerting

### 8.1 Sentry per Error Tracking

```bash
# Installa Sentry SDK nel backend
pip install sentry-sdk[fastapi]
```

```python
# In app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FastApiIntegration()],
    environment=settings.ENVIRONMENT,
    traces_sample_rate=0.1
)
```

### 8.2 Prometheus + Grafana

```yaml
# Aggiungi a docker-compose.yml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 9. Troubleshooting

### 9.1 Container non si avvia

```bash
# Verifica log
docker-compose logs backend

# Verifica configurazione
docker-compose config

# Riavvia servizio specifico
docker-compose restart backend
```

### 9.2 Errori di connessione database

```bash
# Verifica che il database sia in esecuzione
docker-compose ps db

# Testa connessione
docker exec abb_backend python -c "from app.core.database import engine; print(engine.connect())"
```

### 9.3 Frontend non carica

```bash
# Verifica build frontend
docker-compose logs frontend

# Ricostruisci frontend
docker-compose build frontend
docker-compose up -d frontend
```

## 10. Rollback

In caso di problemi dopo un deployment:

```bash
# Torna alla versione precedente
git checkout <previous-commit-hash>

# Rebuild e riavvia
docker-compose build
docker-compose up -d

# Oppure usa backup database
gunzip < /var/backups/abb/backup_YYYYMMDD_HHMMSS.sql.gz | docker exec -i abb_postgres psql -U postgres africa_business_bridge
```

## Conclusione

Seguendo questa guida, la piattaforma Africa Business Bridge sarà deployata in produzione in modo sicuro e scalabile. Ricorda di monitorare regolarmente l'applicazione e di mantenere aggiornati tutti i componenti.

---

**Documento Aggiornato**: Ottobre 2024  
**Versione**: 1.0.0

## Risorse Utili

- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

