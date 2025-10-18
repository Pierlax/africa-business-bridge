"""
Sistema di caching per migliorare le performance delle query frequenti
"""

from functools import wraps
from typing import Any, Callable, Optional
from datetime import datetime, timedelta
import json
import hashlib
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """
    Cache in memoria semplice con TTL (Time To Live).
    Per produzione, considerare Redis per caching distribuito.
    """
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Ottiene un valore dalla cache.
        
        Args:
            key: Chiave del valore
        
        Returns:
            Valore cached o None se non trovato o scaduto
        """
        if key not in self._cache:
            return None
        
        # Verifica scadenza
        if key in self._expiry and datetime.now() > self._expiry[key]:
            self.delete(key)
            return None
        
        logger.debug(f"Cache hit: {key}")
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """
        Salva un valore nella cache.
        
        Args:
            key: Chiave del valore
            value: Valore da cachare
            ttl_seconds: Time to live in secondi (default 5 minuti)
        """
        self._cache[key] = value
        self._expiry[key] = datetime.now() + timedelta(seconds=ttl_seconds)
        logger.debug(f"Cache set: {key} (TTL: {ttl_seconds}s)")
    
    def delete(self, key: str):
        """Rimuove un valore dalla cache"""
        if key in self._cache:
            del self._cache[key]
        if key in self._expiry:
            del self._expiry[key]
        logger.debug(f"Cache delete: {key}")
    
    def clear(self):
        """Svuota completamente la cache"""
        self._cache.clear()
        self._expiry.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self):
        """Rimuove tutti i valori scaduti"""
        now = datetime.now()
        expired_keys = [
            key for key, expiry in self._expiry.items()
            if now > expiry
        ]
        for key in expired_keys:
            self.delete(key)
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")


# Istanza globale del cache
cache = SimpleCache()


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Genera una chiave di cache univoca basata su prefix e parametri.
    
    Args:
        prefix: Prefisso della chiave (es. "market_reports", "news")
        *args: Argomenti posizionali
        **kwargs: Argomenti keyword
    
    Returns:
        Chiave di cache univoca
    """
    # Serializza gli argomenti in modo consistente
    args_str = json.dumps(args, sort_keys=True, default=str)
    kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
    combined = f"{prefix}:{args_str}:{kwargs_str}"
    
    # Genera hash per chiavi più corte
    key_hash = hashlib.md5(combined.encode()).hexdigest()
    return f"{prefix}:{key_hash}"


def cached(ttl_seconds: int = 300, key_prefix: str = "default"):
    """
    Decorator per cachare il risultato di una funzione.
    
    Args:
        ttl_seconds: Time to live in secondi
        key_prefix: Prefisso per la chiave di cache
    
    Example:
        @cached(ttl_seconds=600, key_prefix="market_reports")
        def get_market_reports(country: str):
            # Query pesante al database
            return reports
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Genera chiave di cache
            cache_key = generate_cache_key(key_prefix, *args, **kwargs)
            
            # Prova a ottenere dalla cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Esegui la funzione
            logger.debug(f"Cache miss: {cache_key}")
            result = func(*args, **kwargs)
            
            # Salva in cache
            cache.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key_prefix: str):
    """
    Invalida tutte le chiavi di cache con un certo prefisso.
    
    Args:
        key_prefix: Prefisso delle chiavi da invalidare
    """
    keys_to_delete = [
        key for key in cache._cache.keys()
        if key.startswith(f"{key_prefix}:")
    ]
    for key in keys_to_delete:
        cache.delete(key)
    logger.info(f"Invalidated {len(keys_to_delete)} cache entries with prefix: {key_prefix}")


# Funzione helper per uso in API routes
def cache_response(key: str, data: Any, ttl_seconds: int = 300):
    """
    Funzione helper per cachare risposte API.
    
    Args:
        key: Chiave di cache
        data: Dati da cachare
        ttl_seconds: Time to live in secondi
    """
    cache.set(key, data, ttl_seconds)


def get_cached_response(key: str) -> Optional[Any]:
    """
    Funzione helper per ottenere risposte API cached.
    
    Args:
        key: Chiave di cache
    
    Returns:
        Dati cached o None
    """
    return cache.get(key)

