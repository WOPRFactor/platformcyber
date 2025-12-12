"""
Prometheus Metrics
==================

Definición y tracking de métricas para Prometheus.
"""

import time
from functools import wraps
from typing import Callable, Any
from flask import Flask, request, g
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    multiprocess,
    generate_latest as prom_generate_latest
)
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# MÉTRICAS DE APLICACIÓN
# ============================================================================

# Requests HTTP
http_requests_total = Counter(
    'http_requests_total',
    'Total de requests HTTP recibidas',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'Duración de requests HTTP',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Número de requests HTTP en progreso',
    ['method', 'endpoint']
)

# Scans
scans_total = Counter(
    'scans_total',
    'Total de scans ejecutados',
    ['scan_type', 'status']
)

scans_duration_seconds = Histogram(
    'scans_duration_seconds',
    'Duración de scans',
    ['scan_type'],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600)
)

scans_active = Gauge(
    'scans_active',
    'Número de scans activos',
    ['scan_type']
)

# Vulnerabilidades
vulnerabilities_found = Counter(
    'vulnerabilities_found_total',
    'Total de vulnerabilidades encontradas',
    ['severity', 'category']
)

vulnerabilities_by_severity = Gauge(
    'vulnerabilities_by_severity',
    'Vulnerabilidades por severidad',
    ['severity']
)

# Tareas Celery
celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total de tareas Celery',
    ['task_name', 'status']
)

celery_tasks_duration_seconds = Histogram(
    'celery_tasks_duration_seconds',
    'Duración de tareas Celery',
    ['task_name'],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600)
)

celery_tasks_active = Gauge(
    'celery_tasks_active',
    'Tareas Celery activas',
    ['task_name']
)

celery_queue_length = Gauge(
    'celery_queue_length',
    'Longitud de cola Celery',
    ['queue_name']
)

# Database
database_connections = Gauge(
    'database_connections',
    'Conexiones de base de datos activas'
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Duración de queries de base de datos',
    ['operation'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

# WebSocket
websocket_connections = Gauge(
    'websocket_connections_total',
    'Conexiones WebSocket activas'
)

websocket_messages = Counter(
    'websocket_messages_total',
    'Mensajes WebSocket',
    ['event_type', 'direction']
)

# Errors
errors_total = Counter(
    'errors_total',
    'Total de errores',
    ['error_type', 'endpoint']
)

# Application Info
app_info = Gauge(
    'app_info',
    'Información de la aplicación',
    ['version', 'environment']
)


# ============================================================================
# MIDDLEWARE PARA TRACKING AUTOMÁTICO
# ============================================================================

def setup_metrics(app: Flask) -> None:
    """
    Configura métricas y middleware para tracking automático.
    
    Args:
        app: Instancia de Flask
    """
    
    # Endpoint para Prometheus scraping
    @app.route('/metrics')
    def metrics():
        """Endpoint para Prometheus."""
        return prom_generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    
    # Middleware para tracking de requests
    @app.before_request
    def before_request():
        """Track inicio de request."""
        g.start_time = time.time()
        
        endpoint = request.endpoint or 'unknown'
        method = request.method
        
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
    
    @app.after_request
    def after_request(response):
        """Track fin de request."""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            endpoint = request.endpoint or 'unknown'
            method = request.method
            status = response.status_code
            
            # Decrementar requests en progreso
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
            
            # Incrementar total de requests
            http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
            
            # Registrar duración
            http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
        
        return response
    
    # Handler de errores
    @app.errorhandler(Exception)
    def handle_error(error):
        """Track errores."""
        endpoint = request.endpoint or 'unknown'
        error_type = type(error).__name__
        
        errors_total.labels(error_type=error_type, endpoint=endpoint).inc()
        
        # Re-raise para que Flask lo maneje normalmente
        raise error
    
    # Set app info
    app_info.labels(
        version=app.config.get('VERSION', '3.0.0'),
        environment=app.config.get('ENV', 'development')
    ).set(1)
    
    logger.info("✅ Prometheus metrics configurado")


# ============================================================================
# DECORADORES PARA TRACKING MANUAL
# ============================================================================

def track_request_duration(endpoint_name: str = None):
    """
    Decorator para trackear duración de función.
    
    Args:
        endpoint_name: Nombre del endpoint (opcional)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                name = endpoint_name or func.__name__
                http_request_duration_seconds.labels(
                    method='INTERNAL',
                    endpoint=name
                ).observe(duration)
        
        return wrapper
    return decorator


def track_scan_metrics(scan_type: str):
    """
    Decorator para trackear métricas de scans.
    
    Args:
        scan_type: Tipo de scan (nmap, nuclei, etc.)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Incrementar scans activos
            scans_active.labels(scan_type=scan_type).inc()
            
            start_time = time.time()
            status = 'success'
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'failed'
                raise
            finally:
                # Decrementar scans activos
                scans_active.labels(scan_type=scan_type).dec()
                
                # Registrar duración
                duration = time.time() - start_time
                scans_duration_seconds.labels(scan_type=scan_type).observe(duration)
                
                # Incrementar total
                scans_total.labels(scan_type=scan_type, status=status).inc()
        
        return wrapper
    return decorator


def track_vulnerability_metrics(severity: str, category: str = 'general'):
    """
    Registra vulnerabilidad encontrada.
    
    Args:
        severity: Severidad (critical, high, medium, low, info)
        category: Categoría de vulnerabilidad
    """
    vulnerabilities_found.labels(severity=severity, category=category).inc()
    
    # Actualizar gauge por severidad
    # Nota: Esto requeriría query a DB para count total
    # Por ahora solo incrementamos el counter


def track_celery_metrics(task_name: str, status: str, duration: float = None):
    """
    Registra métrica de tarea Celery.
    
    Args:
        task_name: Nombre de la tarea
        status: Estado (pending, started, success, failure)
        duration: Duración en segundos (opcional)
    """
    celery_tasks_total.labels(task_name=task_name, status=status).inc()
    
    if status == 'started':
        celery_tasks_active.labels(task_name=task_name).inc()
    elif status in ('success', 'failure'):
        celery_tasks_active.labels(task_name=task_name).dec()
        
        if duration is not None:
            celery_tasks_duration_seconds.labels(task_name=task_name).observe(duration)


# ============================================================================
# FUNCIONES HELPER
# ============================================================================

def track_websocket_connection(increment: bool = True):
    """
    Track conexiones WebSocket.
    
    Args:
        increment: True para incrementar, False para decrementar
    """
    if increment:
        websocket_connections.inc()
    else:
        websocket_connections.dec()


def track_websocket_message(event_type: str, direction: str = 'outbound'):
    """
    Track mensaje WebSocket.
    
    Args:
        event_type: Tipo de evento
        direction: 'inbound' o 'outbound'
    """
    websocket_messages.labels(event_type=event_type, direction=direction).inc()


def track_database_query(operation: str, duration: float):
    """
    Track query de base de datos.
    
    Args:
        operation: Tipo de operación (SELECT, INSERT, UPDATE, DELETE)
        duration: Duración en segundos
    """
    database_query_duration_seconds.labels(operation=operation).observe(duration)


def set_database_connections(count: int):
    """
    Set número de conexiones de base de datos.
    
    Args:
        count: Número de conexiones activas
    """
    database_connections.set(count)


def set_celery_queue_length(queue_name: str, length: int):
    """
    Set longitud de cola Celery.
    
    Args:
        queue_name: Nombre de la cola
        length: Longitud de la cola
    """
    celery_queue_length.labels(queue_name=queue_name).set(length)

