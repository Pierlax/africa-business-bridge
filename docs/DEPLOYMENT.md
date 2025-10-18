# Guida al Deployment

Questa guida fornisce istruzioni dettagliate per il deployment della piattaforma Africa Business Bridge in ambiente di produzione.

## Prerequisiti di Produzione

### Server Requirements
- **Sistema Operativo**: Ubuntu 22.04 LTS o superiore
- **CPU**: Minimo 4 core
- **RAM**: Minimo 8GB
- **Storage**: Minimo 100GB SSD
- **Network**: Connessione stabile con IP pubblico

### Software Requirements
- Docker e Docker Compose
- Nginx (reverse proxy)
- PostgreSQL 14+
- Redis 7+
- Certbot (per SSL/TLS)

## Architettura di Deployment

```
Internet
    ↓
Nginx (Reverse Proxy + SSL)
    ↓
    ├── Frontend (React/Next.js) - Port 3000
    └── Backend (FastAPI) - Port 8000
         ↓
         ├── PostgreSQL - Port 5432
         └── Redis - Port 6379
```

## Setup Database PostgreSQL

### 1. Installazione PostgreSQL

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### 2. Configurazione Database

```bash
sudo -u postgres psql

-- Crea il database
CREATE DATABASE africa_business_bridge;

-- Crea l'utente
CREATE USER abb_user WITH PASSWORD 'strong_password_here';

-- Assegna i permessi
GRANT ALL PRIVILEGES ON DATABASE africa_business_bridge TO abb_user;

-- Esci
\q
```

### 3. Configurazione per Connessioni Remote (se necessario)

Modifica `/etc/postgresql/14/main/postgresql.conf`:
```
listen_addresses = 'localhost'  # o '0.0.0.0' per connessioni remote
```

Modifica `/etc/postgresql/14/main/pg_hba.conf`:
```
host    africa_business_bridge    abb_user    127.0.0.1/32    md5
```

Riavvia PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Setup Redis

### 1. Installazione Redis

```bash
sudo apt install redis-server
```

### 2. Configurazione Redis

Modifica `/etc/redis/redis.conf`:
```
bind 127.0.0.1
requirepass your_redis_password
```

Riavvia Redis:
```bash
sudo systemctl restart redis-server
```

## Deployment Backend (FastAPI)

### 1. Preparazione Ambiente

```bash
cd /opt
sudo git clone <repository-url> africa-business-bridge
cd africa-business-bridge/backend

# Crea ambiente virtuale
python3.11 -m venv venv
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt
```

### 2. Configurazione Variabili d'Ambiente

Crea `/opt/africa-business-bridge/backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://abb_user:strong_password_here@localhost:5432/africa_business_bridge

# JWT
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]

# Email (configurare con provider SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@yourdomain.com

# Redis
REDIS_URL=redis://:your_redis_password@localhost:6379/0

# Upload
UPLOAD_DIR=/opt/africa-business-bridge/backend/uploads
MAX_UPLOAD_SIZE=10485760

# API Esterne
ZOOM_API_KEY=your-zoom-api-key
ZOOM_API_SECRET=your-zoom-api-secret
```

### 3. Migrazione Database

```bash
cd /opt/africa-business-bridge/backend
source venv/bin/activate

# Esegui le migrazioni (quando implementate con Alembic)
# alembic upgrade head

# Per ora, le tabelle vengono create automaticamente all'avvio
```

### 4. Setup Systemd Service

Crea `/etc/systemd/system/abb-backend.service`:

```ini
[Unit]
Description=Africa Business Bridge Backend API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/africa-business-bridge/backend
Environment="PATH=/opt/africa-business-bridge/backend/venv/bin"
ExecStart=/opt/africa-business-bridge/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Abilita e avvia il servizio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable abb-backend
sudo systemctl start abb-backend
sudo systemctl status abb-backend
```

## Deployment Frontend (React)

### 1. Build Produzione

```bash
cd /opt/africa-business-bridge/frontend

# Installa dipendenze
pnpm install

# Configura variabili d'ambiente per produzione
echo "VITE_API_URL=https://api.yourdomain.com/api/v1" > .env.production

# Build
pnpm run build
```

### 2. Setup con Nginx o Serve Statico

#### Opzione A: Nginx per File Statici

```bash
sudo cp -r /opt/africa-business-bridge/frontend/dist /var/www/abb-frontend
sudo chown -R www-data:www-data /var/www/abb-frontend
```

#### Opzione B: Server Node.js con PM2

```bash
# Installa PM2 globalmente
npm install -g pm2

# Avvia il server di produzione
cd /opt/africa-business-bridge/frontend
pm2 start "pnpm run preview" --name abb-frontend
pm2 save
pm2 startup
```

## Configurazione Nginx

### 1. Installazione Nginx

```bash
sudo apt install nginx
```

### 2. Configurazione Sito

Crea `/etc/nginx/sites-available/africa-business-bridge`:

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# Frontend
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (da configurare con Certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /var/www/abb-frontend;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Backend API
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (per future implementazioni)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Upload files
    location /uploads {
        alias /opt/africa-business-bridge/backend/uploads;
        expires 1y;
        add_header Cache-Control "public";
    }
}
```

Abilita il sito:
```bash
sudo ln -s /etc/nginx/sites-available/africa-business-bridge /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Setup SSL con Let's Encrypt

```bash
# Installa Certbot
sudo apt install certbot python3-certbot-nginx

# Ottieni certificato SSL
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Il rinnovo automatico è già configurato
sudo certbot renew --dry-run
```

## Backup e Monitoraggio

### 1. Backup Database

Crea script `/opt/scripts/backup-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -U abb_user africa_business_bridge | gzip > $BACKUP_DIR/abb_backup_$DATE.sql.gz

# Mantieni solo gli ultimi 30 giorni
find $BACKUP_DIR -name "abb_backup_*.sql.gz" -mtime +30 -delete
```

Aggiungi a crontab:
```bash
sudo crontab -e
# Aggiungi:
0 2 * * * /opt/scripts/backup-db.sh
```

### 2. Monitoraggio con Logs

```bash
# Logs backend
sudo journalctl -u abb-backend -f

# Logs Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

## Sicurezza

### 1. Firewall (UFW)

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Fail2Ban

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Aggiornamenti Automatici

```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

## Troubleshooting

### Backend non si avvia
```bash
# Controlla i log
sudo journalctl -u abb-backend -n 50

# Verifica connessione database
psql -U abb_user -d africa_business_bridge -h localhost

# Verifica permessi file
sudo chown -R www-data:www-data /opt/africa-business-bridge/backend
```

### Frontend non carica
```bash
# Verifica build
cd /opt/africa-business-bridge/frontend
pnpm run build

# Controlla Nginx
sudo nginx -t
sudo systemctl status nginx
```

### Database lento
```bash
# Analizza query lente
sudo -u postgres psql africa_business_bridge
SELECT * FROM pg_stat_activity WHERE state = 'active';

# Ottimizza database
VACUUM ANALYZE;
```

## Performance Optimization

### 1. Database Indexing
Assicurati che gli indici siano creati sulle colonne più interrogate.

### 2. Redis Caching
Implementa caching per query frequenti e sessioni utente.

### 3. CDN
Considera l'uso di un CDN (CloudFlare, AWS CloudFront) per asset statici.

### 4. Load Balancing
Per traffico elevato, implementa load balancing con più istanze backend.

## Conclusione

Questa guida copre il deployment base della piattaforma. Per ambienti di produzione su larga scala, considera:

- Kubernetes per orchestrazione container
- Database managed (AWS RDS, Google Cloud SQL)
- Object storage (S3, Google Cloud Storage) per file upload
- Monitoring avanzato (Prometheus, Grafana)
- Log aggregation (ELK Stack, Loki)

