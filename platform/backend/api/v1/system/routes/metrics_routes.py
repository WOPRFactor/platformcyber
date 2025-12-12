"""
Metrics Routes
==============

Rutas para métricas del sistema.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
import logging

from repositories import ScanRepository
from models import Scan

logger = logging.getLogger(__name__)


def register_routes(bp: Blueprint):
    """Registra las rutas de métricas."""
    
    @bp.route('/metrics', methods=['GET', 'OPTIONS'], strict_slashes=False)
    @bp.route('/metrics/', methods=['GET', 'OPTIONS'], strict_slashes=False)
    def get_metrics():
        """
        Obtiene métricas del sistema en formato JSON.
        
        Endpoint REST para consumo del frontend y sistema de monitoreo.
        Para métricas Prometheus, usar /metrics directamente.
        
        Returns:
            Métricas del sistema: CPU, RAM, Disk en porcentajes y GB
        """
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request()
        
        try:
            scan_repo = ScanRepository()
            
            all_scans = Scan.query.all()
            running_scans = scan_repo.get_running_scans()
            completed_scans = [s for s in all_scans if s.status == 'completed']
            failed_scans = [s for s in all_scans if s.status == 'failed']
            pending_scans = [s for s in all_scans if s.status in ['pending', 'queued']]
            
            scans_by_type = {}
            scans_by_status = {
                'running': len(running_scans),
                'completed': len(completed_scans),
                'failed': len(failed_scans),
                'pending': len(pending_scans),
                'cancelled': len([s for s in all_scans if s.status == 'cancelled'])
            }
            
            for scan in all_scans:
                scan_type = scan.scan_type
                scans_by_type[scan_type] = scans_by_type.get(scan_type, 0) + 1
            
            system_metrics = {}
            try:
                import psutil
                import platform
                
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_count = psutil.cpu_count()
                
                memory = psutil.virtual_memory()
                memory_total_mb = memory.total / (1024 * 1024)
                memory_used_mb = memory.used / (1024 * 1024)
                memory_available_mb = memory.available / (1024 * 1024)
                memory_percent = memory.percent
                
                disk = psutil.disk_usage('/')
                disk_total_gb = disk.total / (1024 * 1024 * 1024)
                disk_used_gb = disk.used / (1024 * 1024 * 1024)
                disk_free_gb = disk.free / (1024 * 1024 * 1024)
                disk_percent = disk.percent
                
                system_metrics = {
                    'cpu': {
                        'percent': round(cpu_percent, 2),
                        'count': cpu_count
                    },
                    'memory': {
                        'total_mb': round(memory_total_mb, 2),
                        'used_mb': round(memory_used_mb, 2),
                        'available_mb': round(memory_available_mb, 2),
                        'percent': round(memory_percent, 2)
                    },
                    'disk': {
                        'total_gb': round(disk_total_gb, 2),
                        'used_gb': round(disk_used_gb, 2),
                        'free_gb': round(disk_free_gb, 2),
                        'percent': round(disk_percent, 2)
                    },
                    'platform': platform.system(),
                    'python_version': platform.python_version()
                }
            except ImportError:
                import platform
                logger.warning("psutil no disponible, métricas de sistema no incluidas")
                system_metrics = {
                    'error': 'psutil no disponible',
                    'platform': platform.system(),
                    'python_version': platform.python_version()
                }
            except Exception as e:
                logger.error(f"Error obteniendo métricas de sistema: {e}")
                system_metrics = {'error': str(e)}
            
            avg_duration = None
            if completed_scans:
                durations = []
                for scan in completed_scans:
                    if scan.started_at and scan.completed_at:
                        duration = (scan.completed_at - scan.started_at).total_seconds()
                        durations.append(duration)
                if durations:
                    avg_duration = sum(durations) / len(durations)
            
            return jsonify({
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'scans': {
                    'total': len(all_scans),
                    'active': len(running_scans),
                    'by_status': scans_by_status,
                    'by_type': scans_by_type,
                    'avg_duration_seconds': round(avg_duration, 2) if avg_duration else None
                },
                'system': system_metrics,
                'uptime_seconds': None
            }), 200
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


