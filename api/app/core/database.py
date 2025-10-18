from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Creazione engine del database
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Creazione session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class per i modelli
Base = declarative_base()


def get_db():
    """
    Dependency per ottenere una sessione del database.
    Utilizzata nelle route FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

