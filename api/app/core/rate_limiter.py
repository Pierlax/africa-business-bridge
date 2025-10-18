"""
Middleware per rate limiting delle richieste API
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter semplice basato su memoria.
    Per produzione, considerare Redis per rate limiting distribuito.
    """
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = timedelta(minutes=5)
        self.last_cleanup = datetime.now()
    
    def _cleanup_old_requests(self):
        """Rimuove le richieste vecchie per liberare memoria"""
        if datetime.now() - self.last_cleanup > self.cleanup_interval:
            cutoff_time = datetime.now() - timedelta(minutes=1)
            for ip in list(self.requests.keys()):
                self.requests[ip] = [
                    req_time for req_time in self.requests[ip]
                    if req_time > cutoff_time
                ]
                if not self.requests[ip]:
                    del self.requests[ip]
            self.last_cleanup = datetime.now()
    
    def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        """
        Verifica se la richiesta è permessa.
        
        Args:
            client_ip: Indirizzo IP del client
        
        Returns:
            Tuple[bool, int]: (is_allowed, remaining_requests)
        """
        self._cleanup_old_requests()
        
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=1)
        
        # Filtra richieste nell'ultimo minuto
        recent_requests = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff_time
        ]
        
        if len(recent_requests) >= self.requests_per_minute:
            return False, 0
        
        # Aggiungi la richiesta corrente
        self.requests[client_ip] = recent_requests + [now]
        remaining = self.requests_per_minute - len(self.requests[client_ip])
        
        return True, remaining


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware FastAPI per rate limiting.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.rate_limiter = RateLimiter(requests_per_minute)
        self.excluded_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Escludi alcuni path dal rate limiting
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Ottieni IP del client
        client_ip = request.client.host
        
        # Verifica rate limit
        is_allowed, remaining = self.rate_limiter.is_allowed(client_ip)
        
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": 60
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.rate_limiter.requests_per_minute),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        # Processa la richiesta
        response = await call_next(request)
        
        # Aggiungi header rate limit
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response


# Rate limiter più restrittivo per endpoint sensibili
class StrictRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiter più restrittivo per endpoint sensibili (login, register).
    """
    
    def __init__(self, app, requests_per_minute: int = 10):
        super().__init__(app)
        self.rate_limiter = RateLimiter(requests_per_minute)
        self.sensitive_paths = [
            "/api/v1/auth/login",
            "/api/v1/auth/register"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Applica solo a path sensibili
        if not any(request.url.path == path for path in self.sensitive_paths):
            return await call_next(request)
        
        client_ip = request.client.host
        is_allowed, remaining = self.rate_limiter.is_allowed(client_ip)
        
        if not is_allowed:
            logger.warning(f"Strict rate limit exceeded for IP: {client_ip} on path: {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many authentication attempts. Please try again later.",
                    "retry_after": 60
                },
                headers={
                    "Retry-After": "60"
                }
            )
        
        response = await call_next(request)
        return response

