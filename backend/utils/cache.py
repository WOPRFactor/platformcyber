"""
Cache Utilities
===============

Redis caching layer para optimización de performance.
"""

import json
import hashlib
from functools import wraps
from typing import Any, Callable, Optional
import redis
import logging

logger = logging.getLogger(__name__)

# Redis client (inicializado en runtime)
redis_client: Optional[redis.Redis] = None


def init_cache(redis_url: str = 'redis://localhost:6379/2') -> None:
    """
    Inicializa cliente Redis para caching.
    
    Args:
        redis_url: URL de conexión a Redis
    """
    global redis_client
    try:
        redis_client = redis.from_url(redis_url, decode_responses=True)
        redis_client.ping()
        logger.info(f"✅ Redis cache conectado: {redis_url}")
    except Exception as e:
        logger.error(f"❌ Error conectando a Redis: {e}")
        redis_client = None


def cache_key(*args, **kwargs) -> str:
    """
    Genera cache key único basado en argumentos.
    
    Args:
        *args: Argumentos posicionales
        **kwargs: Argumentos nombrados
    
    Returns:
        Cache key MD5
    """
    key_data = f"{args}_{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(
    ttl: int = 300,
    prefix: str = 'cache',
    key_func: Optional[Callable] = None
):
    """
    Decorator para cachear resultados de funciones.
    
    Args:
        ttl: Time-to-live en segundos (default: 5 minutos)
        prefix: Prefijo para cache key
        key_func: Función custom para generar cache key
    
    Example:
        @cached(ttl=600, prefix='scan_results')
        def get_scan_results(scan_id):
            return expensive_query(scan_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Si Redis no está disponible, ejecutar función directamente
            if redis_client is None:
                return func(*args, **kwargs)
            
            # Generar cache key
            if key_func:
                key = f"{prefix}:{key_func(*args, **kwargs)}"
            else:
                key = f"{prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            try:
                # Intentar obtener de cache
                cached_value = redis_client.get(key)
                if cached_value is not None:
                    logger.debug(f"💾 Cache HIT: {key}")
                    return json.loads(cached_value)
                
                # Cache MISS - ejecutar función
                logger.debug(f"🔄 Cache MISS: {key}")
                result = func(*args, **kwargs)
                
                # Guardar en cache
                redis_client.setex(
                    key,
                    ttl,
                    json.dumps(result, default=str)
                )
                
                return result
                
            except Exception as e:
                logger.error(f"❌ Cache error: {e}")
                # En caso de error, ejecutar función sin cache
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str) -> int:
    """
    Invalida cache keys que coincidan con patrón.
    
    Args:
        pattern: Patrón Redis (ej: 'scan_results:*')
    
    Returns:
        Número de keys eliminadas
    """
    if redis_client is None:
        return 0
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            count = redis_client.delete(*keys)
            logger.info(f"🗑️  Cache invalidado: {count} keys ({pattern})")
            return count
        return 0
    except Exception as e:
        logger.error(f"❌ Error invalidando cache: {e}")
        return 0


def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    """
    Set valor en cache.
    
    Args:
        key: Cache key
        value: Valor a cachear
        ttl: Time-to-live en segundos
    
    Returns:
        True si exitoso
    """
    if redis_client is None:
        return False
    
    try:
        redis_client.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception as e:
        logger.error(f"❌ Error setting cache: {e}")
        return False


def cache_get(key: str) -> Optional[Any]:
    """
    Get valor de cache.
    
    Args:
        key: Cache key
    
    Returns:
        Valor cacheado o None
    """
    if redis_client is None:
        return None
    
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"❌ Error getting cache: {e}")
        return None


def cache_delete(key: str) -> bool:
    """
    Elimina key de cache.
    
    Args:
        key: Cache key
    
    Returns:
        True si exitoso
    """
    if redis_client is None:
        return False
    
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"❌ Error deleting cache: {e}")
        return False


def cache_stats() -> dict:
    """
    Obtiene estadísticas de cache.
    
    Returns:
        Dict con estadísticas
    """
    if redis_client is None:
        return {'status': 'disconnected'}
    
    try:
        info = redis_client.info('stats')
        return {
            'status': 'connected',
            'total_keys': redis_client.dbsize(),
            'hits': info.get('keyspace_hits', 0),
            'misses': info.get('keyspace_misses', 0),
            'hit_rate': (
                info.get('keyspace_hits', 0) / 
                (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1))
                * 100
            )
        }
    except Exception as e:
        logger.error(f"❌ Error getting cache stats: {e}")
        return {'status': 'error', 'error': str(e)}

