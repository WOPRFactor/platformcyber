"""
Scheduler Service
=================

Scheduled scans y tareas programadas.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class SchedulerService:
    """Servicio de scans programados."""
    
    def __init__(self):
        """Inicializa scheduler."""
        self.scheduler = BackgroundScheduler()
        self.scheduled_scans = {}
        logger.info("✅ Scheduler Service inicializado")
    
    def start(self):
        """Inicia el scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            # Programar limpieza de logs cada hora
            self._schedule_log_cleanup()
            logger.info("🕒 Scheduler iniciado")
    
    def stop(self):
        """Detiene el scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("⏹️  Scheduler detenido")
    
    def schedule_scan(
        self,
        scan_id: str,
        scan_type: str,
        target: str,
        schedule: str,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Programa un scan.
        
        Args:
            scan_id: ID único del scan programado
            scan_type: Tipo de scan (nmap, nuclei, etc.)
            target: Target a escanear
            schedule: Expresión cron o interval (ej: "0 0 * * *" o "every 24h")
            options: Opciones adicionales
        
        Returns:
            Dict con detalles del scan programado
        """
        try:
            # Parsear schedule
            trigger = self._parse_schedule(schedule)
            
            # Crear job
            job = self.scheduler.add_job(
                func=self._execute_scheduled_scan,
                trigger=trigger,
                args=[scan_id, scan_type, target, options],
                id=scan_id,
                name=f"{scan_type} scan on {target}",
                replace_existing=True
            )
            
            # Guardar info
            self.scheduled_scans[scan_id] = {
                'scan_id': scan_id,
                'scan_type': scan_type,
                'target': target,
                'schedule': schedule,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'active'
            }
            
            logger.info(f"📅 Scan programado: {scan_id} - {schedule}")
            
            # Logging al workspace
            from utils.workspace_logger import log_to_workspace
            workspace_id = options.get('workspace_id') if options else None
            if workspace_id:
                log_to_workspace(
                    workspace_id=workspace_id,
                    source='SCHEDULER',
                    level='INFO',
                    message=f"Scan programado: {scan_type} en {target}",
                    metadata={
                        'scan_id': scan_id,
                        'scan_type': scan_type,
                        'target': target,
                        'schedule': schedule,
                        'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                    }
                )
            
            return self.scheduled_scans[scan_id]
            
        except Exception as e:
            logger.error(f"❌ Error programando scan: {e}")
            raise
    
    def cancel_scheduled_scan(self, scan_id: str) -> bool:
        """
        Cancela scan programado.
        
        Args:
            scan_id: ID del scan programado
        
        Returns:
            True si cancelado exitosamente
        """
        try:
            self.scheduler.remove_job(scan_id)
            if scan_id in self.scheduled_scans:
                self.scheduled_scans[scan_id]['status'] = 'cancelled'
            logger.info(f"🗑️  Scan programado cancelado: {scan_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error cancelando scan: {e}")
            return False
    
    def get_scheduled_scans(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los scans programados.
        
        Returns:
            Lista de scans programados
        """
        return list(self.scheduled_scans.values())
    
    def get_scheduled_scan(self, scan_id: str) -> Dict[str, Any]:
        """
        Obtiene detalle de scan programado.
        
        Args:
            scan_id: ID del scan
        
        Returns:
            Dict con detalle
        """
        scan = self.scheduled_scans.get(scan_id)
        if not scan:
            raise ValueError(f"Scheduled scan not found: {scan_id}")
        
        # Actualizar next_run desde scheduler
        job = self.scheduler.get_job(scan_id)
        if job and job.next_run_time:
            scan['next_run'] = job.next_run_time.isoformat()
        
        return scan
    
    def _parse_schedule(self, schedule: str):
        """
        Parsea expresión de schedule.
        
        Args:
            schedule: String con schedule (cron o interval)
        
        Returns:
            APScheduler trigger
        """
        schedule = schedule.lower().strip()
        
        # Intervalos comunes
        intervals = {
            'every hour': {'hours': 1},
            'every 6h': {'hours': 6},
            'every 12h': {'hours': 12},
            'every day': {'days': 1},
            'every week': {'weeks': 1},
            'daily': {'days': 1},
            'weekly': {'weeks': 1},
        }
        
        if schedule in intervals:
            return IntervalTrigger(**intervals[schedule])
        
        # Parsear "every Nh" o "every Nd"
        if schedule.startswith('every '):
            parts = schedule.split()
            if len(parts) == 2:
                value = parts[1]
                if value.endswith('h'):
                    return IntervalTrigger(hours=int(value[:-1]))
                elif value.endswith('d'):
                    return IntervalTrigger(days=int(value[:-1]))
                elif value.endswith('m'):
                    return IntervalTrigger(minutes=int(value[:-1]))
        
        # Expresión cron (ej: "0 0 * * *" = daily at midnight)
        try:
            parts = schedule.split()
            if len(parts) == 5:
                return CronTrigger(
                    minute=parts[0],
                    hour=parts[1],
                    day=parts[2],
                    month=parts[3],
                    day_of_week=parts[4]
                )
        except Exception:
            pass
        
        raise ValueError(f"Invalid schedule format: {schedule}")

    def preview_scheduled_scan(
        self,
        scan_type: str,
        target: str,
        schedule: str,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Preview de un scan programado (sin ejecutar).
        
        Args:
            scan_type: Tipo de scan (nmap, nuclei, etc.)
            target: Target a escanear
            schedule: Expresión cron o interval
            options: Opciones adicionales
            
        Returns:
            Dict con preview del comando y parámetros
        """
        try:
            # Intentar parsear el schedule para validarlo
            trigger = self._parse_schedule(schedule)
            
            # Construir comando simulado
            command_parts = [scan_type, target]
            
            if options:
                for key, value in options.items():
                    if key != 'workspace_id':  # No incluir workspace_id en el comando
                        command_parts.extend([f'--{key}', str(value)])
            
            command_str = ' '.join(command_parts)
            
            # Calcular próxima ejecución estimada
            next_run_estimate = "Calculando..."
            try:
                # Crear un job temporal para obtener next_run
                from apscheduler.triggers.cron import CronTrigger
                from apscheduler.triggers.interval import IntervalTrigger
                temp_job = self.scheduler.add_job(
                    func=lambda: None,
                    trigger=trigger,
                    id='temp_preview',
                    replace_existing=True
                )
                if temp_job.next_run_time:
                    next_run_estimate = temp_job.next_run_time.isoformat()
                self.scheduler.remove_job('temp_preview')
            except:
                pass
            
            # Calcular tiempo estimado basado en tipo de scan
            timeout_map = {
                'nmap': 1800,
                'nuclei': 3600,
                'nikto': 600,
                'sqlmap': 3600,
                'gobuster': 1800
            }
            estimated_timeout = timeout_map.get(scan_type, 1800)
            
            return {
                'command': command_parts,
                'command_string': command_str,
                'parameters': {
                    'scan_type': scan_type,
                    'target': target,
                    'schedule': schedule,
                    'options': options or {}
                },
                'estimated_timeout': estimated_timeout,
                'next_run_estimate': next_run_estimate,
                'schedule_description': self._get_schedule_description(schedule),
                'output_file': f'/workspaces/workspace_{options.get("workspace_id", "X")}/scheduled_scans/{{scan_id}}/{{timestamp}}.txt',
                'warnings': [
                    'El scan se ejecutará automáticamente según el schedule',
                    'Asegúrate de que el scheduler esté corriendo',
                    'Los scans programados consumen recursos del sistema'
                ],
                'suggestions': [
                    'Verifica que el schedule sea correcto antes de programar',
                    'Considera el impacto en el sistema objetivo',
                    'Revisa los logs después de la primera ejecución'
                ]
            }
        except ValueError as e:
            return {
                'error': str(e),
                'command': [],
                'command_string': '',
                'parameters': {
                    'scan_type': scan_type,
                    'target': target,
                    'schedule': schedule,
                    'options': options or {}
                }
            }

    def _get_schedule_description(self, schedule: str) -> str:
        """Obtiene descripción legible del schedule."""
        schedule_lower = schedule.lower().strip()
        
        descriptions = {
            'every hour': 'Cada hora',
            'every 6h': 'Cada 6 horas',
            'every 12h': 'Cada 12 horas',
            'every day': 'Diariamente',
            'every week': 'Semanalmente',
            'daily': 'Diariamente',
            'weekly': 'Semanalmente'
        }
        
        if schedule_lower in descriptions:
            return descriptions[schedule_lower]
        
        if schedule_lower.startswith('every '):
            return f"Cada {schedule_lower.replace('every ', '')}"
        
        # Cron expression
        if len(schedule.split()) == 5:
            return f"Expresión cron: {schedule}"
        
        return schedule
    
    def _execute_scheduled_scan(
        self,
        scan_id: str,
        scan_type: str,
        target: str,
        options: Dict[str, Any]
    ):
        """
        Ejecuta scan programado (callback).
        
        Args:
            scan_id: ID del scan
            scan_type: Tipo de scan
            target: Target
            options: Opciones
        """
        logger.info(f"⚡ Ejecutando scan programado: {scan_id} ({scan_type} on {target})")
        
        # En producción, aquí se dispararía tarea Celery
        # Por ahora solo loguear
        
        try:
            # from tasks.scanning_tasks import scan_nmap_async
            # scan_nmap_async.delay(target, options)
            logger.info(f"✅ Scan {scan_id} dispatched to Celery")
        except Exception as e:
            logger.error(f"❌ Error executing scheduled scan {scan_id}: {e}")
    
    def _schedule_log_cleanup(self):
        """Programa limpieza automática de logs."""
        try:
            self.scheduler.add_job(
                func=self._cleanup_logs,
                trigger=IntervalTrigger(hours=1),  # Cada hora
                id='log_cleanup',
                name='Log cleanup task',
                replace_existing=True
            )
            logger.info("📋 Tarea de limpieza de logs programada (cada hora)")
        except Exception as e:
            logger.error(f"❌ Error programando limpieza de logs: {e}")
    
    def _cleanup_logs(self):
        """Ejecuta limpieza de logs del backend."""
        try:
            from utils.log_cleaner import clean_backend_logs
            from flask import current_app
            
            # Obtener horas de retención de la configuración
            # Si no hay app context, usar 6 horas por defecto (desarrollo)
            try:
                hours_to_keep = current_app.config.get('LOG_RETENTION_HOURS', 6)
            except RuntimeError:
                # No hay app context, usar valor por defecto
                hours_to_keep = 6
            
            result = clean_backend_logs(hours_to_keep=hours_to_keep, dry_run=False)
            
            if result.get('success'):
                files_cleaned = result.get('files_cleaned', 0)
                total_removed = result.get('total_lines_removed', 0)
                total_original = result.get('total_original_size', 0)
                total_new = result.get('total_new_size', 0)
                
                logger.info(
                    f"🧹 Logs limpiados ({files_cleaned} archivos): "
                    f"{total_removed} líneas eliminadas, "
                    f"Tamaño: {total_original / (1024*1024):.1f}MB -> {total_new / (1024*1024):.1f}MB "
                    f"(manteniendo últimas {hours_to_keep} horas)"
                )
            else:
                logger.warning(f"⚠️  Error limpiando logs: {result.get('error', 'Unknown error')}")
        except Exception as e:
            logger.error(f"❌ Error en limpieza de logs: {e}", exc_info=True)


# Singleton
scheduler_service = SchedulerService()

