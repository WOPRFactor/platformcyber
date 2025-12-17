#!/bin/bash
# Script para reiniciar workers de Celery

echo "🔄 Deteniendo workers de Celery..."

# Buscar y detener todos los procesos de Celery worker
pkill -f "celery.*worker.*celery_dev4"

# Esperar a que se detengan
sleep 2

echo "✅ Workers detenidos"
echo "🚀 Iniciando nuevos workers..."

# Cambiar al directorio del backend
cd "$(dirname "$0")"

# Activar entorno virtual e iniciar workers
source venv/bin/activate

# Iniciar worker en background
nohup python -m celery -A celery_app.celery worker \
    --hostname=celery_dev4@kali \
    --loglevel=info \
    --concurrency=2 \
    > celery_worker.log 2>&1 &

echo "✅ Workers reiniciados"
echo "📋 PID del nuevo worker: $!"
echo ""
echo "Para verificar que la tarea está registrada, ejecuta:"
echo "  python -c \"from celery_app import celery; inspect = celery.control.inspect(); registered = inspect.registered(); print([t for w, tasks in registered.items() for t in tasks if 'reporting' in t])\""

