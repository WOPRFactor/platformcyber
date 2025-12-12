"""
WebSocket Events Emitters
=========================

Funciones helper para emitir eventos desde servicios/tasks.
"""

from flask_socketio import emit
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def emit_scan_progress(
    scan_id: str,
    workspace_id: int,
    progress: int,
    status: str,
    message: str = "",
    data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Emitir progreso de un scan.
    
    Args:
        scan_id: ID único del scan
        workspace_id: ID del workspace
        progress: Porcentaje de progreso (0-100)
        status: Estado del scan (running, completed, failed)
        message: Mensaje descriptivo
        data: Datos adicionales (hosts, puertos, etc.)
    """
    from websockets import socketio
    
    payload = {
        'scan_id': scan_id,
        'workspace_id': workspace_id,
        'progress': progress,
        'status': status,
        'message': message,
        'timestamp': __import__('time').time()
    }
    
    if data:
        payload['data'] = data
    
    # Emitir a la sala del scan
    socketio.emit(
        'scan_progress',
        payload,
        room=f'scan_{scan_id}'
    )
    
    # También emitir a la sala del workspace
    socketio.emit(
        'scan_progress',
        payload,
        room=f'workspace_{workspace_id}'
    )
    
    logger.debug(f"📡 Scan progress emitted: {scan_id} - {progress}%")


def emit_vulnerability_found(
    workspace_id: int,
    vulnerability: Dict[str, Any],
    scan_id: Optional[str] = None
) -> None:
    """
    Emitir cuando se encuentra una vulnerabilidad.
    
    Args:
        workspace_id: ID del workspace
        vulnerability: Datos de la vulnerabilidad
        scan_id: ID del scan (opcional)
    """
    from websockets import socketio
    
    payload = {
        'workspace_id': workspace_id,
        'vulnerability': vulnerability,
        'timestamp': __import__('time').time()
    }
    
    if scan_id:
        payload['scan_id'] = scan_id
        socketio.emit('vuln_found', payload, room=f'scan_{scan_id}')
    
    socketio.emit('vuln_found', payload, room=f'workspace_{workspace_id}')
    
    severity = vulnerability.get('severity', 'unknown').upper()
    logger.info(f"🚨 Vulnerability found [{severity}]: {vulnerability.get('name', 'Unknown')}")


def emit_task_update(
    task_id: str,
    workspace_id: int,
    status: str,
    progress: Optional[int] = None,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
) -> None:
    """
    Emitir actualización de tarea Celery.
    
    Args:
        task_id: ID de la tarea Celery
        workspace_id: ID del workspace
        status: Estado de la tarea (PENDING, STARTED, SUCCESS, FAILURE)
        progress: Progreso opcional (0-100)
        result: Resultado de la tarea (si completada)
        error: Mensaje de error (si falló)
    """
    from websockets import socketio
    
    payload = {
        'task_id': task_id,
        'workspace_id': workspace_id,
        'status': status,
        'timestamp': __import__('time').time()
    }
    
    if progress is not None:
        payload['progress'] = progress
    
    if result:
        payload['result'] = result
    
    if error:
        payload['error'] = error
    
    socketio.emit('task_update', payload, room=f'workspace_{workspace_id}')
    
    logger.debug(f"📋 Task update emitted: {task_id} - {status}")


def emit_notification(
    workspace_id: int,
    title: str,
    message: str,
    level: str = "info",
    data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Emitir notificación general.
    
    Args:
        workspace_id: ID del workspace
        title: Título de la notificación
        message: Mensaje
        level: Nivel (info, success, warning, error)
        data: Datos adicionales
    """
    from websockets import socketio
    
    payload = {
        'workspace_id': workspace_id,
        'title': title,
        'message': message,
        'level': level,
        'timestamp': __import__('time').time()
    }
    
    if data:
        payload['data'] = data
    
    socketio.emit('notification', payload, room=f'workspace_{workspace_id}')
    
    logger.info(f"🔔 Notification [{level}]: {title}")


def emit_log_entry(
    workspace_id: int,
    log_level: str,
    source: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Emitir entrada de log en tiempo real.
    
    Args:
        workspace_id: ID del workspace
        log_level: Nivel del log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        source: Origen del log (nmap, nuclei, etc.)
        message: Mensaje del log
        data: Datos adicionales
    """
    from websockets import socketio
    
    payload = {
        'workspace_id': workspace_id,
        'level': log_level,
        'source': source,
        'message': message,
        'timestamp': __import__('time').time()
    }
    
    if data:
        payload['data'] = data
    
    socketio.emit('log_entry', payload, room=f'workspace_{workspace_id}')
    
    logger.debug(f"📝 Log entry emitted: [{source}] {message[:50]}...")


def emit_backend_log(
    workspace_id: int,
    level: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Emitir log del backend Flask.
    
    Args:
        workspace_id: ID del workspace
        level: Nivel del log (DEBUG, INFO, WARNING, ERROR)
        message: Mensaje del log
        data: Datos adicionales
    """
    from websockets import socketio
    
    payload = {
        'source': 'BACKEND',
        'level': level.upper(),
        'message': message,
        'timestamp': __import__('time').time(),
        'workspace_id': workspace_id
    }
    
    if data:
        payload['data'] = data
    
    socketio.emit('backend_log', payload, room=f'workspace_{workspace_id}')
    logger.debug(f"📝 Backend log emitted: [{level}] {message[:50]}...")


def emit_celery_log(
    workspace_id: int,
    level: str,
    message: str,
    task_id: Optional[str] = None
) -> None:
    """
    Emitir log de Celery worker.
    
    Args:
        workspace_id: ID del workspace
        level: Nivel del log (DEBUG, INFO, WARNING, ERROR)
        message: Mensaje del log
        task_id: ID de la tarea Celery (opcional)
    """
    from websockets import socketio
    
    payload = {
        'source': 'CELERY',
        'level': level.upper(),
        'message': message,
        'timestamp': __import__('time').time(),
        'workspace_id': workspace_id
    }
    
    if task_id:
        payload['task_id'] = task_id
    
    socketio.emit('celery_log', payload, room=f'workspace_{workspace_id}')
    logger.debug(f"📝 Celery log emitted: [{level}] {message[:50]}...")


def emit_tool_log(
    workspace_id: int,
    tool: str,
    level: str,
    message: str,
    command: Optional[str] = None
) -> None:
    """
    Emitir log de herramienta (nikto, nmap, nuclei, etc.).
    
    Args:
        workspace_id: ID del workspace
        tool: Nombre de la herramienta (nikto, nmap, nuclei, etc.)
        level: Nivel del log (DEBUG, INFO, WARNING, ERROR)
        message: Mensaje del log
        command: Comando ejecutado (opcional, para mostrar "$ nikto -h ...")
    """
    from websockets import socketio
    
    payload = {
        'source': tool.upper(),  # NIKTO, NMAP, NUCLEI, etc.
        'level': level.upper(),
        'message': message,
        'timestamp': __import__('time').time(),
        'workspace_id': workspace_id
    }
    
    if command:
        payload['command'] = command
    
    socketio.emit('tool_log', payload, room=f'workspace_{workspace_id}')
    logger.debug(f"📝 Tool log emitted: [{tool.upper()}] {message[:50]}...")


def emit_scan_completed(
    scan_id: str,
    workspace_id: int,
    tool: str,
    duration: float,
    findings_count: int,
    results: Optional[Dict[str, Any]] = None
) -> None:
    """
    Emitir cuando un scan se completa.
    
    Args:
        scan_id: ID del scan
        workspace_id: ID del workspace
        tool: Herramienta utilizada
        duration: Duración en segundos
        findings_count: Cantidad de hallazgos
        results: Resultados resumidos
    """
    from websockets import socketio
    
    payload = {
        'scan_id': scan_id,
        'workspace_id': workspace_id,
        'tool': tool,
        'duration': duration,
        'findings_count': findings_count,
        'timestamp': __import__('time').time()
    }
    
    if results:
        payload['results'] = results
    
    socketio.emit('scan_completed', payload, room=f'scan_{scan_id}')
    socketio.emit('scan_completed', payload, room=f'workspace_{workspace_id}')
    
    logger.info(f"✅ Scan completed: {tool} - {findings_count} findings in {duration:.2f}s")


def emit_port_discovered(
    workspace_id: int,
    host: str,
    port: int,
    service: str,
    scan_id: Optional[str] = None
) -> None:
    """
    Emitir cuando se descubre un puerto abierto.
    
    Args:
        workspace_id: ID del workspace
        host: IP o hostname
        port: Número de puerto
        service: Servicio detectado
        scan_id: ID del scan (opcional)
    """
    from websockets import socketio
    
    payload = {
        'workspace_id': workspace_id,
        'host': host,
        'port': port,
        'service': service,
        'timestamp': __import__('time').time()
    }
    
    if scan_id:
        payload['scan_id'] = scan_id
        socketio.emit('port_discovered', payload, room=f'scan_{scan_id}')
    
    socketio.emit('port_discovered', payload, room=f'workspace_{workspace_id}')
    
    logger.debug(f"🔓 Port discovered: {host}:{port} ({service})")


def emit_exploit_attempt(
    workspace_id: int,
    target: str,
    exploit: str,
    status: str,
    message: str = "",
    result: Optional[Dict[str, Any]] = None
) -> None:
    """
    Emitir intento de explotación.
    
    Args:
        workspace_id: ID del workspace
        target: Target del exploit
        exploit: Nombre del exploit
        status: Estado (attempting, success, failed)
        message: Mensaje descriptivo
        result: Resultado del exploit
    """
    from websockets import socketio
    
    payload = {
        'workspace_id': workspace_id,
        'target': target,
        'exploit': exploit,
        'status': status,
        'message': message,
        'timestamp': __import__('time').time()
    }
    
    if result:
        payload['result'] = result
    
    socketio.emit('exploit_attempt', payload, room=f'workspace_{workspace_id}')
    
    status_emoji = {
        'attempting': '🎯',
        'success': '💥',
        'failed': '❌'
    }.get(status, '🔧')
    
    logger.info(f"{status_emoji} Exploit {status}: {exploit} -> {target}")


def emit_report_generated(
    workspace_id: int,
    report_id: str,
    report_type: str,
    file_path: str,
    file_size: int
) -> None:
    """
    Emitir cuando se genera un reporte.
    
    Args:
        workspace_id: ID del workspace
        report_id: ID del reporte
        report_type: Tipo de reporte (pdf, html, json)
        file_path: Ruta del archivo generado
        file_size: Tamaño del archivo en bytes
    """
    from websockets import socketio
    
    payload = {
        'workspace_id': workspace_id,
        'report_id': report_id,
        'report_type': report_type,
        'file_path': file_path,
        'file_size': file_size,
        'timestamp': __import__('time').time()
    }
    
    socketio.emit('report_generated', payload, room=f'workspace_{workspace_id}')
    
    logger.info(f"📄 Report generated: {report_type} - {file_size / 1024:.2f} KB")


__all__ = [
    'emit_scan_progress',
    'emit_vulnerability_found',
    'emit_log_entry',
    'emit_backend_log',
    'emit_celery_log',
    'emit_tool_log',
    'emit_task_update',
    'emit_notification',
    'emit_log_entry',
    'emit_scan_completed',
    'emit_port_discovered',
    'emit_exploit_attempt',
    'emit_report_generated'
]

