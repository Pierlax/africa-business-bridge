from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configurazione principale dell'applicazione.
    Le variabili d'ambiente possono essere definite in un file .env
    """
    
    # Configurazione generale
    PROJECT_NAME: str = "Africa Business Bridge"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Configurazione database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/africa_business_bridge"
    
    # Configurazione JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Configurazione CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # Configurazione email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    
    # Configurazione Redis (per cache e Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Configurazione upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Configurazione API esterne
    ZOOM_API_KEY: Optional[str] = None
    ZOOM_API_SECRET: Optional[str] = None
    GOOGLE_MEET_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

