# Guida Completa al Deployment su Google Cloud Platform - Africa Business Bridge

## Introduzione

Questo documento fornisce istruzioni complete e dettagliate per deployare la piattaforma Africa Business Bridge su Google Cloud Platform (GCP). Sono disponibili due approcci: uno manuale e uno automatizzato con Terraform.

**Informazioni Progetto:**
- **Project ID**: nimble-service-475513-s1
- **Region**: europe-west1
- **Dominio**: africabusinessbridge.it
- **Email SSL**: edoardo.ciech@gmail.com
- **Service Account**: manus-ai@nimble-service-475513-s1.iam.gserviceaccount.com

## Prerequisiti

Prima di iniziare, assicurati di avere:

1. **Account Google Cloud Platform** attivo con il progetto creato
2. **Credenziali GCP** in formato JSON (già fornite)
3. **Dominio registrato** (africabusinessbridge.it)
4. **Accesso al DNS** del dominio per configurare i record
5. **gcloud CLI** installato (opzionale, ma consigliato)
6. **Terraform** installato (se usi l'approccio automatizzato)

## Approccio 1: Deployment Manuale

### Fase 1: Autenticazione con GCP

```bash
# Imposta le credenziali GCP
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/nimble-service-475513-s1-c1ccfe02f98a.json"

# Verifica autenticazione
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
gcloud config set project nimble-service-475513-s1

# Verifica che tutto sia configurato correttamente
gcloud auth list
gcloud config list
```

### Fase 2: Creazione del Database PostgreSQL su Cloud SQL

```bash
# Crea istanza Cloud SQL PostgreSQL
gcloud sql instances create africa-business-bridge-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=europe-west1 \
  --availability-type=REGIONAL \
  --backup-start-time=02:00 \
  --enable-bin-log \
  --storage-auto-increase \
  --storage-auto-increase-limit=100 \
  --labels=environment=production,app=africa-business-bridge

# Attendi il completamento (circa 5-10 minuti)
gcloud sql instances describe africa-business-bridge-db --region=europe-west1

# Crea il database
gcloud sql databases create africa_business_bridge \
  --instance=africa-business-bridge-db

# Crea l'utente del database
gcloud sql users create abb_user \
  --instance=africa-business-bridge-db \
  --password=$(openssl rand -base64 32)

# Salva la password in un file sicuro
gcloud sql users describe abb_user --instance=africa-business-bridge-db
```

**Nota**: Salva la password generata in un luogo sicuro. La utilizzerai nella configurazione dell'applicazione.

### Fase 3: Creazione di Cloud Storage Bucket

```bash
# Crea bucket per gli upload
gsutil mb -l europe-west1 gs://abb-uploads-nimble-service-475513-s1

# Configura CORS per permettere richieste dal frontend
cat > cors.json << 'EOF'
[
  {
    "origin": ["https://africabusinessbridge.it"],
    "method": ["GET", "HEAD", "DELETE", "POST", "PUT"],
    "responseHeader": ["Content-Type", "x-goog-meta-*"],
    "maxAgeSeconds": 3600
  }
]
EOF

gsutil cors set cors.json gs://abb-uploads-nimble-service-475513-s1

# Configura versioning per il bucket
gsutil versioning set on gs://abb-uploads-nimble-service-475513-s1

# Configura lifecycle policy (mantieni solo le ultime 3 versioni)
cat > lifecycle.json << 'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"numNewerVersions": 3}
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://abb-uploads-nimble-service-475513-s1
```

### Fase 4: Preparazione e Deploy del Backend su Cloud Run

```bash
# Naviga alla directory del backend
cd /home/ubuntu/africa-business-bridge/backend

# Genera SECRET_KEY sicuro
SECRET_KEY=$(openssl rand -hex 32)
echo "SECRET_KEY=$SECRET_KEY" > .env.production

# Ottieni la password del database (salvata precedentemente)
DB_PASSWORD="YOUR_DB_PASSWORD_HERE"

# Crea file di configurazione per Cloud Run
cat > app.yaml << EOF
runtime: python311
env: standard
entrypoint: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

env_variables:
  ENVIRONMENT: "production"
  DATABASE_URL: "postgresql://abb_user:${DB_PASSWORD}@/africa_business_bridge?host=/cloudsql/nimble-service-475513-s1:europe-west1:africa-business-bridge-db"
  SECRET_KEY: "${SECRET_KEY}"
  BACKEND_CORS_ORIGINS: "https://africabusinessbridge.it"
  UPLOAD_DIR: "gs://abb-uploads-nimble-service-475513-s1"

automatic_scaling:
  min_instances: 1
  max_instances: 10
EOF

# Deploy su Cloud Run
gcloud run deploy africa-business-bridge-backend \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="postgresql://abb_user:${DB_PASSWORD}@/africa_business_bridge?host=/cloudsql/nimble-service-475513-s1:europe-west1:africa-business-bridge-db" \
  --set-env-vars SECRET_KEY="${SECRET_KEY}" \
  --set-env-vars ENVIRONMENT="production" \
  --set-env-vars BACKEND_CORS_ORIGINS="https://africabusinessbridge.it" \
  --set-env-vars UPLOAD_DIR="gs://abb-uploads-nimble-service-475513-s1" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 3600 \
  --max-instances 10 \
  --service-account manus-ai@nimble-service-475513-s1.iam.gserviceaccount.com

# Ottieni l'URL del servizio
BACKEND_URL=$(gcloud run services describe africa-business-bridge-backend --region europe-west1 --format='value(status.url)')
echo "Backend URL: $BACKEND_URL"
```

### Fase 5: Preparazione e Deploy del Frontend su Cloud Run

```bash
# Naviga alla directory del frontend
cd /home/ubuntu/africa-business-bridge/frontend

# Crea file .env per il build
cat > .env.production << EOF
VITE_API_URL=https://api.africabusinessbridge.it/api/v1
EOF

# Build dell'applicazione React
npm run build

# Deploy su Cloud Run
gcloud run deploy africa-business-bridge-frontend \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 256Mi \
  --cpu 1 \
  --max-instances 5

# Ottieni l'URL del servizio
FRONTEND_URL=$(gcloud run services describe africa-business-bridge-frontend --region europe-west1 --format='value(status.url)')
echo "Frontend URL: $FRONTEND_URL"
```

### Fase 6: Configurazione del DNS

Accedi al tuo provider DNS (Cloudflare, Route53, ecc.) e configura i seguenti record:

**Record A/CNAME:**
- **Nome**: africabusinessbridge.it
- **Valore**: URL del servizio frontend (ottenuto sopra)
- **TTL**: 300

**Record A/CNAME per API:**
- **Nome**: api.africabusinessbridge.it
- **Valore**: URL del servizio backend (ottenuto sopra)
- **TTL**: 300

**Esempio con Cloudflare:**
```
africabusinessbridge.it          CNAME   africa-business-bridge-frontend-xxxxx-ew.a.run.app
api.africabusinessbridge.it      CNAME   africa-business-bridge-backend-xxxxx-ew.a.run.app
```

### Fase 7: Configurazione SSL/TLS

**Opzione A: Cloudflare (Consigliato)**

Se usi Cloudflare come DNS provider:

1. Accedi a Cloudflare Dashboard
2. Seleziona il dominio africabusinessbridge.it
3. Vai a SSL/TLS > Overview
4. Seleziona "Full (strict)" per SSL/TLS encryption
5. Cloudflare genererà automaticamente un certificato

**Opzione B: Let's Encrypt con Cloud Armor**

```bash
# Crea certificato SSL con Let's Encrypt
certbot certonly --manual \
  -d africabusinessbridge.it \
  -d api.africabusinessbridge.it \
  -d www.africabusinessbridge.it \
  --preferred-challenges dns

# Carica il certificato su GCP
gcloud compute ssl-certificates create abb-ssl-cert \
  --certificate=/etc/letsencrypt/live/africabusinessbridge.it/fullchain.pem \
  --private-key=/etc/letsencrypt/live/africabusinessbridge.it/privkey.pem \
  --global
```

### Fase 8: Verifica del Deployment

```bash
# Verifica che i servizi Cloud Run siano in esecuzione
gcloud run services list --region europe-west1

# Test dell'API backend
curl https://api.africabusinessbridge.it/health

# Test del frontend
curl https://africabusinessbridge.it/

# Verifica del database
gcloud sql instances describe africa-business-bridge-db

# Verifica del bucket storage
gsutil ls -l gs://abb-uploads-nimble-service-475513-s1
```

## Approccio 2: Deployment Automatizzato con Terraform

### Fase 1: Installazione di Terraform

```bash
# Scarica Terraform (se non già installato)
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verifica installazione
terraform --version
```

### Fase 2: Preparazione dei File Terraform

```bash
# Naviga alla directory terraform
cd /home/ubuntu/africa-business-bridge/terraform

# Copia il file di esempio
cp terraform.tfvars.example terraform.tfvars

# Modifica terraform.tfvars con i tuoi valori
nano terraform.tfvars

# Genera password sicure
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -hex 32)

# Aggiungi a terraform.tfvars
echo "db_password = \"$DB_PASSWORD\"" >> terraform.tfvars
echo "secret_key  = \"$SECRET_KEY\"" >> terraform.tfvars
```

### Fase 3: Esecuzione di Terraform

```bash
# Inizializza Terraform
terraform init

# Valida la configurazione
terraform validate

# Visualizza il piano di deployment
terraform plan -out=tfplan

# Applica il piano
terraform apply tfplan

# Salva gli output
terraform output -json > outputs.json
```

### Fase 4: Configurazione del DNS (come sopra)

Utilizza gli output di Terraform per configurare i record DNS.

## Monitoring e Logging

### Configurazione di Cloud Logging

```bash
# Visualizza log del backend
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=africa-business-bridge-backend" \
  --limit 50 \
  --format json

# Streaming log in tempo reale
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=africa-business-bridge-backend" \
  --limit 50 \
  --format json \
  --follow
```

### Configurazione di Cloud Monitoring

```bash
# Crea dashboard di monitoraggio
gcloud monitoring dashboards create --config-from-file=- << 'EOF'
{
  "displayName": "Africa Business Bridge",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Backend CPU Usage",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\" resource.label.service_name=\"africa-business-bridge-backend\""
                }
              }
            }]
          }
        }
      }
    ]
  }
}
EOF
```

## Backup e Disaster Recovery

### Backup Automatici del Database

```bash
# Cloud SQL gestisce automaticamente i backup
# Verifica configurazione backup
gcloud sql instances describe africa-business-bridge-db \
  --format='value(settings.backupConfiguration)'

# Crea backup manuale
gcloud sql backups create \
  --instance=africa-business-bridge-db \
  --description="Manual backup before major update"

# Elenca backup
gcloud sql backups list --instance=africa-business-bridge-db
```

### Backup del Cloud Storage

```bash
# Abilita versioning (già fatto sopra)
# Crea backup completo
gsutil -m cp -r gs://abb-uploads-nimble-service-475513-s1 gs://abb-backups-$(date +%Y%m%d)
```

## Troubleshooting

### Errore: "Cloud SQL instance not found"

```bash
# Verifica che l'istanza sia stata creata
gcloud sql instances list

# Se non esiste, ricrea con il comando della Fase 2
```

### Errore: "Permission denied" durante il deploy

```bash
# Verifica i permessi del Service Account
gcloud projects get-iam-policy nimble-service-475513-s1 \
  --flatten="bindings[].members" \
  --filter="bindings.members:manus-ai@*"

# Aggiungi ruoli necessari se mancanti
gcloud projects add-iam-policy-binding nimble-service-475513-s1 \
  --member=serviceAccount:manus-ai@nimble-service-475513-s1.iam.gserviceaccount.com \
  --role=roles/run.admin
```

### Errore: "Connection refused" dal frontend al backend

```bash
# Verifica che CORS sia configurato correttamente
curl -H "Origin: https://africabusinessbridge.it" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -X OPTIONS https://api.africabusinessbridge.it/api/v1/auth/login -v

# Verifica che il backend sia raggiungibile
curl https://api.africabusinessbridge.it/health
```

## Manutenzione Continua

### Aggiornamenti dell'Applicazione

```bash
# Per aggiornare il backend
cd backend
git pull origin main
gcloud run deploy africa-business-bridge-backend \
  --source . \
  --region europe-west1

# Per aggiornare il frontend
cd ../frontend
git pull origin main
npm run build
gcloud run deploy africa-business-bridge-frontend \
  --source . \
  --region europe-west1
```

### Scaling Automatico

Cloud Run scala automaticamente in base al traffico. Per modificare i limiti:

```bash
gcloud run services update africa-business-bridge-backend \
  --min-instances=2 \
  --max-instances=20 \
  --region europe-west1
```

### Costi e Ottimizzazione

Per ridurre i costi:

1. **Ridurre le istanze minime** quando il traffico è basso
2. **Usare Cloud Storage per asset statici** anziché servire dal backend
3. **Abilitare Cloud CDN** per cache globale
4. **Monitorare l'utilizzo** con Cloud Billing

## Conclusione

La piattaforma Africa Business Bridge è ora deployata su Google Cloud Platform con:

✅ Database PostgreSQL gestito su Cloud SQL  
✅ Backend FastAPI su Cloud Run  
✅ Frontend React su Cloud Run  
✅ Storage per upload su Cloud Storage  
✅ SSL/TLS con certificato valido  
✅ Logging e monitoring configurati  
✅ Backup automatici abilitati  
✅ Scaling automatico configurato  

Per supporto aggiuntivo, consulta la documentazione ufficiale di GCP o contatta il team di sviluppo.

---

**Documento Aggiornato**: Ottobre 2024  
**Versione**: 1.0.0  
**Stato**: Pronto per Produzione

