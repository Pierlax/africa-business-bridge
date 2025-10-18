from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging

from .core.settings import settings
from .core.database import engine, Base
from .core.rate_limiter import RateLimitMiddleware, StrictRateLimitMiddleware
from .api import auth, expo, matching, market, training

# Configurazione logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crea le tabelle del database
Base.metadata.create_all(bind=engine)

# Inizializza l'applicazione FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API per la piattaforma Africa Business Bridge",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    debug=settings.DEBUG
)

logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} in {settings.ENVIRONMENT} mode")

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Aggiungi GZip compression se abilitato
if settings.ENABLE_GZIP:
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    logger.info("GZip compression enabled")

# Aggiungi Rate Limiting se abilitato
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)
    app.add_middleware(StrictRateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_AUTH_PER_MINUTE)
    logger.info(f"Rate limiting enabled: {settings.RATE_LIMIT_PER_MINUTE} req/min (general), {settings.RATE_LIMIT_AUTH_PER_MINUTE} req/min (auth)")

# Crea la directory per gli upload se non esiste
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Monta la directory degli upload come static files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Registra i router
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(expo.router, prefix=settings.API_V1_STR)
app.include_router(matching.router, prefix=settings.API_V1_STR)
app.include_router(market.router, prefix=settings.API_V1_STR)
app.include_router(training.router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    """Endpoint root dell'API"""
    return {
        "message": f"Benvenuto su {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/api/docs"
    }


@app.get("/health")
def health_check():
    """Endpoint per health check (utile per load balancers e monitoring)"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "features": {
            "rate_limiting": settings.RATE_LIMIT_ENABLED,
            "caching": settings.CACHE_ENABLED,
            "gzip": settings.ENABLE_GZIP
        }
    }


@app.on_event("startup")
async def startup_event():
    """Evento eseguito all'avvio dell'applicazione"""
    logger.info("Application startup complete")
    logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[-1]}")  # Log solo host/db, non credenziali


@app.on_event("shutdown")
async def shutdown_event():
    """Evento eseguito alla chiusura dell'applicazione"""
    logger.info("Application shutdown")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower()
    )

