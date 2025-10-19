"""
Redis Caching Module for Africa Business Bridge

This module provides utilities for caching frequently accessed data using Redis,
including decorators for automatic caching of API endpoints and database queries.
"""

import json
import functools
from typing import Any, Callable, Optional
from datetime import timedelta
import redis
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Redis client instance
redis_client: Optional[redis.Redis] = None


def init_redis(redis_url: str = "redis://localhost:6379/0") -> redis.Redis:
    """
    Initialize Redis client connection.
    
    Args:
        redis_url: Redis connection URL
        
    Returns:
        Redis client instance
    """
    global redis_client
    try:
        redis_client = redis.from_url(redis_url, decode_responses=True)
        redis_client.ping()
        logger.info("Redis connection established successfully")
        return redis_client
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        redis_client = None
        return None


def get_redis_client() -> Optional[redis.Redis]:
    """Get the Redis client instance."""
    return redis_client


def cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a cache key from prefix and arguments.
    
    Args:
        prefix: Cache key prefix
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Generated cache key
    """
    key_parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        if isinstance(arg, (str, int, float)):
            key_parts.append(str(arg))
    
    # Add keyword arguments
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (str, int, float)):
            key_parts.append(f"{k}:{v}")
    
    return ":".join(key_parts)


def cached(
    prefix: str,
    ttl: int = 3600,
    key_builder: Optional[Callable] = None
) -> Callable:
    """
    Decorator for caching function results in Redis.
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (default: 1 hour)
        key_builder: Optional custom key builder function
        
    Returns:
        Decorator function
        
    Example:
        @cached(prefix="market_reports", ttl=3600)
        async def get_market_reports(country: str):
            # Function implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            if redis_client is None:
                # If Redis is not available, execute function normally
                return await func(*args, **kwargs)
            
            try:
                # Generate cache key
                if key_builder:
                    cache_k = key_builder(*args, **kwargs)
                else:
                    cache_k = cache_key(prefix, *args, **kwargs)
                
                # Try to get from cache
                cached_value = redis_client.get(cache_k)
                if cached_value:
                    logger.debug(f"Cache hit for key: {cache_k}")
                    return json.loads(cached_value)
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Store in cache
                redis_client.setex(
                    cache_k,
                    timedelta(seconds=ttl),
                    json.dumps(result, default=str)
                )
                logger.debug(f"Cached result for key: {cache_k}")
                
                return result
            except Exception as e:
                logger.error(f"Cache error: {e}")
                # On error, execute function normally
                return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            if redis_client is None:
                return func(*args, **kwargs)
            
            try:
                # Generate cache key
                if key_builder:
                    cache_k = key_builder(*args, **kwargs)
                else:
                    cache_k = cache_key(prefix, *args, **kwargs)
                
                # Try to get from cache
                cached_value = redis_client.get(cache_k)
                if cached_value:
                    logger.debug(f"Cache hit for key: {cache_k}")
                    return json.loads(cached_value)
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Store in cache
                redis_client.setex(
                    cache_k,
                    timedelta(seconds=ttl),
                    json.dumps(result, default=str)
                )
                logger.debug(f"Cached result for key: {cache_k}")
                
                return result
            except Exception as e:
                logger.error(f"Cache error: {e}")
                return func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def invalidate_cache(pattern: str) -> int:
    """
    Invalidate cache keys matching a pattern.
    
    Args:
        pattern: Key pattern (supports wildcards)
        
    Returns:
        Number of keys deleted
    """
    if redis_client is None:
        return 0
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            deleted = redis_client.delete(*keys)
            logger.info(f"Invalidated {deleted} cache keys matching pattern: {pattern}")
            return deleted
        return 0
    except Exception as e:
        logger.error(f"Error invalidating cache: {e}")
        return 0


def get_cache_stats() -> dict:
    """
    Get Redis cache statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    if redis_client is None:
        return {"status": "Redis not available"}
    
    try:
        info = redis_client.info()
        return {
            "status": "connected",
            "used_memory": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "total_commands_processed": info.get("total_commands_processed"),
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"status": "error", "message": str(e)}


# Import asyncio for async detection
import asyncio

