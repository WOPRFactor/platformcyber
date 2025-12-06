"""
Scans Management Routes
======================

Rutas para gestión de escaneos (running, cancel, cancel-all).
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from datetime import datetime, timezone
import logging
import os
import signal
import time

from repositories import ScanRepository
from utils.workspace_logger import log_to_workspace

logger = logging.getLogger(__name__)


def register_routes(bp: Blueprint):
    """Registra las rutas de gestión de escaneos."""
    
    @bp.route('/running-scans', methods=['GET', 'OPTIONS'])
    def get_running_scans():
        """
        Obtiene todos los scans en estado 'running'.
        
        Returns:
            Lista de scans con información detallada
        """
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request()
        
        try:
            scan_repo = ScanRepository()
            running_scans = scan_repo.get_running_scans()
            
            scans_data = []
            for scan in running_scans:
                elapsed_time = None
                if scan.started_at:
                    try:
                        if scan.started_at.tzinfo is None:
                            from datetime import timezone as tz
                            started_at_aware = scan.started_at.replace(tzinfo=tz.utc)
                        else:
                            started_at_aware = scan.started_at
                        
                        elapsed = datetime.now(timezone.utc) - started_at_aware
                        elapsed_time = {
                            'hours': elapsed.total_seconds() / 3600,
                            'minutes': elapsed.total_seconds() / 60,
                            'seconds': elapsed.total_seconds()
                        }
                    except Exception as e:
                        logger.warning(f"Error calculando elapsed_time para scan {scan.id}: {e}")
                        elapsed_time = None
                
                scans_data.append({
                    'id': scan.id,
                    'scan_type': scan.scan_type,
                    'target': scan.target,
                    'workspace_id': scan.workspace_id,
                    'user_id': scan.user_id,
                    'started_at': scan.started_at.isoformat() if scan.started_at else None,
                    'progress': scan.progress,
                    'options': scan.options,
                    'elapsed_time': elapsed_time,
                    'tool': scan.options.get('tool') if scan.options else None
                })
            
            return jsonify({
                'scans': scans_data,
                'total': len(scans_data)
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting running scans: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/scans/<int:scan_id>/cancel', methods=['POST'])
    @jwt_required()
    def cancel_scan(scan_id: int):
        """
        Cancela un scan en ejecución o pendiente.
        
        Args:
            scan_id: ID del scan a cancelar
        
        Returns:
            Confirmación de cancelación
        """
        try:
            scan_repo = ScanRepository()
            scan = scan_repo.find_by_id(scan_id)
            
            if not scan:
                return jsonify({'error': 'Scan not found'}), 404
            
            cancellable_states = ['running', 'pending', 'queued']
            
            if scan.status in ['completed', 'failed', 'cancelled']:
                return jsonify({
                    'error': f'Scan cannot be cancelled (current status: {scan.status})',
                    'scan_id': scan_id,
                    'current_status': scan.status
                }), 400
            
            if scan.status not in cancellable_states:
                logger.warning(f"Attempted to cancel scan {scan_id} with unexpected status: {scan.status}")
            
            process_terminated = False
            pid = scan.options.get('pid') if scan.options else None
            
            if not pid and scan.status == 'running' and scan.options:
                tool = scan.options.get('tool', '')
                target = scan.target
                
                try:
                    import subprocess
                    if 'dnsenum' in tool.lower():
                        result = subprocess.run(
                            ['pgrep', '-f', f'dnsenum.*{target}'],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            pids = result.stdout.strip().split('\n')
                            if pids:
                                pid = int(pids[0])
                                logger.info(f"Found process PID {pid} for scan {scan_id} by command search")
                                scan_repo.update_options(scan, {'pid': pid})
                    elif 'amass' in tool.lower():
                        result = subprocess.run(
                            ['pgrep', '-f', f'amass.*{target}'],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            pids = result.stdout.strip().split('\n')
                            if pids:
                                pid = int(pids[0])
                                logger.info(f"Found process PID {pid} for scan {scan_id} by command search")
                                scan_repo.update_options(scan, {'pid': pid})
                except Exception as e:
                    logger.warning(f"Error searching for process by command: {e}")
            
            if pid and scan.status == 'running':
                try:
                    os.kill(pid, 0)
                    
                    try:
                        os.kill(pid, signal.SIGTERM)
                        logger.info(f"Sent SIGTERM to process {pid} for scan {scan_id}")
                        
                        time.sleep(2)
                        
                        try:
                            os.kill(pid, 0)
                            logger.warning(f"Process {pid} still running, sending SIGKILL")
                            os.kill(pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        
                        try:
                            import psutil
                            parent = psutil.Process(pid)
                            children = parent.children(recursive=True)
                            for child in children:
                                try:
                                    child.terminate()
                                    logger.info(f"Terminated child process {child.pid} of scan {scan_id}")
                                except psutil.NoSuchProcess:
                                    pass
                            gone, alive = psutil.wait_procs(children, timeout=3)
                            for child in alive:
                                child.kill()
                                logger.warning(f"Killed child process {child.pid} of scan {scan_id}")
                        except (psutil.NoSuchProcess, ImportError):
                            pass
                        
                        process_terminated = True
                        logger.info(f"Terminated process {pid} and children for scan {scan_id}")
                    except ProcessLookupError:
                        logger.warning(f"Process {pid} not found for scan {scan_id}")
                        process_terminated = True
                except ProcessLookupError:
                    logger.warning(f"Process {pid} not found for scan {scan_id}")
                except PermissionError:
                    logger.warning(f"Permission denied to terminate process {pid} for scan {scan_id}")
                except Exception as e:
                    logger.error(f"Error terminating process {pid}: {e}", exc_info=True)
            
            scan_repo.update_status(scan, 'cancelled', 'Cancelled by user')
            
            log_to_workspace(
                workspace_id=scan.workspace_id,
                source='SYSTEM',
                level='WARNING',
                message=f"Scan {scan_id} ({scan.scan_type}) cancelado por el usuario",
                metadata={
                    'scan_id': scan_id,
                    'scan_type': scan.scan_type,
                    'target': scan.target,
                    'process_terminated': process_terminated,
                    'pid': pid,
                    'previous_status': scan.status
                }
            )
            
            return jsonify({
                'message': 'Scan cancelled successfully',
                'scan_id': scan_id,
                'process_terminated': process_terminated,
                'previous_status': scan.status
            }), 200
            
        except Exception as e:
            logger.error(f"Error cancelling scan {scan_id}: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    
    @bp.route('/scans/cancel-all', methods=['POST'])
    @jwt_required()
    def cancel_all_scans():
        """
        Cancela todos los scans en ejecución o pendientes.
        
        Returns:
            Resumen de cancelaciones realizadas
        """
        try:
            scan_repo = ScanRepository()
            running_scans = scan_repo.get_running_scans()
            
            if not running_scans:
                return jsonify({
                    'message': 'No running scans to cancel',
                    'cancelled': 0,
                    'failed': 0,
                    'total': 0
                }), 200
            
            cancelled_count = 0
            failed_count = 0
            cancelled_ids = []
            failed_ids = []
            
            for scan in running_scans:
                try:
                    cancellable_states = ['running', 'pending', 'queued']
                    
                    if scan.status in ['completed', 'failed', 'cancelled']:
                        continue
                    
                    process_terminated = False
                    pid = scan.options.get('pid') if scan.options else None
                    
                    if not pid and scan.status == 'running' and scan.options:
                        tool = scan.options.get('tool', '')
                        target = scan.target
                        
                        try:
                            import subprocess
                            if 'dnsenum' in tool.lower():
                                result = subprocess.run(
                                    ['pgrep', '-f', f'dnsenum.*{target}'],
                                    capture_output=True,
                                    text=True
                                )
                                if result.returncode == 0 and result.stdout.strip():
                                    pids = result.stdout.strip().split('\n')
                                    if pids:
                                        pid = int(pids[0])
                                        scan_repo.update_options(scan, {'pid': pid})
                            elif 'amass' in tool.lower():
                                result = subprocess.run(
                                    ['pgrep', '-f', f'amass.*{target}'],
                                    capture_output=True,
                                    text=True
                                )
                                if result.returncode == 0 and result.stdout.strip():
                                    pids = result.stdout.strip().split('\n')
                                    if pids:
                                        pid = int(pids[0])
                                        scan_repo.update_options(scan, {'pid': pid})
                        except Exception as e:
                            logger.warning(f"Error searching for process by command for scan {scan.id}: {e}")
                    
                    if pid and scan.status == 'running':
                        try:
                            os.kill(pid, 0)
                            
                            try:
                                os.kill(pid, signal.SIGTERM)
                                logger.info(f"Sent SIGTERM to process {pid} for scan {scan.id}")
                                
                                time.sleep(1)
                                
                                try:
                                    os.kill(pid, 0)
                                    logger.warning(f"Process {pid} still running, sending SIGKILL")
                                    os.kill(pid, signal.SIGKILL)
                                except ProcessLookupError:
                                    pass
                                
                                try:
                                    import psutil
                                    parent = psutil.Process(pid)
                                    children = parent.children(recursive=True)
                                    for child in children:
                                        try:
                                            child.terminate()
                                        except psutil.NoSuchProcess:
                                            pass
                                    gone, alive = psutil.wait_procs(children, timeout=2)
                                    for child in alive:
                                        child.kill()
                                except (psutil.NoSuchProcess, ImportError):
                                    pass
                                
                                process_terminated = True
                            except ProcessLookupError:
                                logger.warning(f"Process {pid} not found for scan {scan.id}")
                                process_terminated = True
                        except ProcessLookupError:
                            logger.warning(f"Process {pid} not found for scan {scan.id}")
                        except PermissionError:
                            logger.warning(f"Permission denied to terminate process {pid} for scan {scan.id}")
                        except Exception as e:
                            logger.error(f"Error terminating process {pid} for scan {scan.id}: {e}")
                    
                    scan_repo.update_status(scan, 'cancelled', 'Cancelled by user (cancel all)')
                    
                    log_to_workspace(
                        workspace_id=scan.workspace_id,
                        source='SYSTEM',
                        level='WARNING',
                        message=f"Scan {scan.id} ({scan.scan_type}) cancelado (cancelación masiva)",
                        metadata={
                            'scan_id': scan.id,
                            'scan_type': scan.scan_type,
                            'target': scan.target,
                            'process_terminated': process_terminated,
                            'pid': pid,
                            'previous_status': scan.status
                        }
                    )
                    
                    cancelled_count += 1
                    cancelled_ids.append(scan.id)
                    
                except Exception as e:
                    logger.error(f"Error cancelling scan {scan.id}: {e}", exc_info=True)
                    failed_count += 1
                    failed_ids.append(scan.id)
            
            return jsonify({
                'message': f'Cancelled {cancelled_count} scan(s)',
                'cancelled': cancelled_count,
                'failed': failed_count,
                'total': len(running_scans),
                'cancelled_ids': cancelled_ids,
                'failed_ids': failed_ids
            }), 200
            
        except Exception as e:
            logger.error(f"Error cancelling all scans: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


