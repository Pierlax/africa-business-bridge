"""
Configurazione avanzata per ambienti multipli (development, staging, production)
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache
import os


class Settings(BaseSettings):
    """
    Configurazione dell'applicazione con supporto per ambienti multipli.
    """
    
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    
    # Application
    APP_NAME: str = "Africa Business Bridge"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/africa_business_bridge"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10
    
    # Caching
    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL: int = 300  # 5 minuti
    CACHE_REPORTS_TTL: int = 3600  # 1 ora
    CACHE_NEWS_TTL: int = 600  # 10 minuti
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    ALLOWED_DOCUMENT_EXTENSIONS: List[str] = [".pdf", ".doc", ".docx", ".xls", ".xlsx"]
    
    # Email (per future implementazioni)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # External Services
    NEWS_SCRAPER_ENABLED: bool = True
    NEWS_SCRAPER_INTERVAL_HOURS: int = 6
    
    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE: Optional[str] = None
    
    # Performance
    ENABLE_GZIP: bool = True
    ENABLE_QUERY_OPTIMIZATION: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def is_production(self) -> bool:
        """Verifica se l'ambiente è production"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Verifica se l'ambiente è development"""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_staging(self) -> bool:
        """Verifica se l'ambiente è staging"""
        return self.ENVIRONMENT == "staging"


class DevelopmentSettings(Settings):
    """Configurazione per ambiente di sviluppo"""
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    RATE_LIMIT_ENABLED: bool = False
    CACHE_ENABLED: bool = False


class StagingSettings(Settings):
    """Configurazione per ambiente di staging"""
    ENVIRONMENT: str = "staging"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    RATE_LIMIT_ENABLED: bool = True
    CACHE_ENABLED: bool = True


class ProductionSettings(Settings):
    """Configurazione per ambiente di produzione"""
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    RATE_LIMIT_ENABLED: bool = True
    CACHE_ENABLED: bool = True
    ENABLE_GZIP: bool = True
    
    # In production, questi dovrebbero essere letti da variabili d'ambiente
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE-THIS-IN-PRODUCTION")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # CORS più restrittivo in production
    BACKEND_CORS_ORIGINS: List[str] = [
        os.getenv("FRONTEND_URL", "https://africabusinessbridge.com")
    ]


@lru_cache()
def get_settings() -> Settings:
    """
    Factory function per ottenere le impostazioni corrette in base all'ambiente.
    Usa lru_cache per evitare di ricreare l'oggetto ad ogni chiamata.
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "staging":
        return StagingSettings()
    else:
        return DevelopmentSettings()


# Istanza globale delle impostazioni
settings = get_settings()

