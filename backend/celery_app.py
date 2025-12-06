"""
Celery Application
==================

Configuración de Celery para procesamiento asíncrono de tareas.

Características:
- Redis como broker y backend
- Serialización JSON
- Timeout configurable por tarea
- Retry automático en fallos
- Task routing por tipo
"""

import os
from celery import Celery
from celery.schedules import crontab


def get_flask_app():
    """Obtiene la instancia de Flask app para contexto en tareas Celery."""
    import sys
    from pathlib import Path
    from flask import Flask
    
    # Asegurar que el directorio backend esté en el path
    backend_dir = Path(__file__).resolve().parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    from config import get_config
    from models import db
    
    app = Flask(__name__)
    config = get_config(os.getenv('FLASK_ENV', 'development'))
    app.config.from_object(config)
    db.init_app(app)  # Inicializar SQLAlchemy con la app
    
    return app

# Configuración desde environment
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
BROKER_URL = os.getenv('CELERY_BROKER_URL', REDIS_URL)
BACKEND_URL = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)

# Crear instancia de Celery
celery = Celery(
    'pentesting_platform',
    broker=BROKER_URL,
    backend=BACKEND_URL
)

# Configuración
celery.conf.update(
    # Serialización
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone
    timezone='America/Argentina/Buenos_Aires',
    enable_utc=True,
    
    # Task execution
    task_track_started=True,
    task_time_limit=3600,  # 1 hora max por defecto
    task_soft_time_limit=3300,  # 55 minutos soft limit
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Worker
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Results
    result_expires=86400,  # 24 horas
    result_persistent=True,
    
    # Retry
    task_default_retry_delay=60,  # 1 minuto
    task_max_retries=3,
    
    # Logging
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
    
    # Task routing
    task_routes={
        'tasks.scanning.*': {'queue': 'scanning'},
        'tasks.exploitation.*': {'queue': 'exploitation'},
        'tasks.ad.*': {'queue': 'active_directory'},
        'tasks.reporting.*': {'queue': 'reporting'},
        'tasks.mobile.*': {'queue': 'mobile'},
        'tasks.container.*': {'queue': 'container'},
        'tasks.brute_force.*': {'queue': 'exploitation'},  # Usa la cola de exploitation
        'tasks.maintenance.*': {'queue': 'reporting'},  # Usa la cola de reporting
    },
    
    # Scheduled tasks (Celery Beat)
    beat_schedule={
        # Limpieza de scans viejos cada día a las 3 AM
        'cleanup-old-scans': {
            'task': 'tasks.maintenance_tasks.cleanup_old_scans',
            'schedule': crontab(hour=3, minute=0),
        },
        # Verificar health de workers cada 5 minutos
        'worker-health-check': {
            'task': 'tasks.maintenance_tasks.worker_health_check',
            'schedule': crontab(minute='*/5'),
        },
    },
)

# Auto-discover tasks manualmente
from tasks import scanning_tasks, exploitation_tasks, ad_tasks, reporting_tasks, mobile_tasks, container_tasks, brute_force_tasks


@celery.task(bind=True)
def debug_task(self):
    """Task de debug para verificar que Celery funciona."""
    print(f'Request: {self.request!r}')
    return {'status': 'ok', 'worker': self.request.hostname}


# Handlers de eventos
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup de tareas periódicas adicionales."""
    # Ejemplo: agregar tareas dinámicas
    pass


@celery.on_after_finalize.connect
def setup_task_routes(sender, **kwargs):
    """Setup de rutas de tareas."""
    pass



