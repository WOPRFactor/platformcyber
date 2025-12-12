"""
Network Routes
=============

Rutas para monitoreo de red.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Importar psutil para métricas de red
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil no disponible. Endpoints de red no funcionarán correctamente.")


def register_routes(bp: Blueprint):
    """Registra las rutas de red."""
    
    @bp.route('/network/metrics/', methods=['GET'], strict_slashes=False)
    @bp.route('/network/metrics', methods=['GET'], strict_slashes=False)
    @jwt_required()
    def get_network_metrics():
        """
        Obtiene métricas agregadas de red del sistema.
        
        Returns:
            JSON con métricas de red
        """
        if not PSUTIL_AVAILABLE:
            return jsonify({
                'error': 'psutil no disponible',
                'message': 'La librería psutil no está instalada. Instalar con: pip install psutil>=5.9.0'
            }), 503
        
        try:
            interfaces = []
            total_bytes_sent = 0
            total_bytes_recv = 0
            total_packets_sent = 0
            total_packets_recv = 0
            
            try:
                net_io = psutil.net_io_counters(pernic=True)
                net_if_stats = psutil.net_if_stats()
            except Exception as e:
                logger.error(f"Error obteniendo estadísticas de interfaces: {e}")
                return jsonify({
                    'error': 'Error obteniendo estadísticas de red',
                    'message': str(e)
                }), 500
            
            for interface_name, stats in net_io.items():
                if_stats = net_if_stats.get(interface_name, {})
                
                interface_data = {
                    "name": interface_name,
                    "bytes_sent": stats.bytes_sent,
                    "bytes_recv": stats.bytes_recv,
                    "packets_sent": stats.packets_sent,
                    "packets_recv": stats.packets_recv,
                    "errin": stats.errin,
                    "errout": stats.errout,
                    "dropin": stats.dropin,
                    "dropout": stats.dropout,
                    "is_up": if_stats.get("isup", False) if if_stats else False
                }
                
                interfaces.append(interface_data)
                
                total_bytes_sent += stats.bytes_sent
                total_bytes_recv += stats.bytes_recv
                total_packets_sent += stats.packets_sent
                total_packets_recv += stats.packets_recv
            
            connections = []
            active_connections = 0
            
            try:
                net_connections_list = psutil.net_connections(kind='inet')
            except (psutil.AccessDenied, PermissionError) as e:
                logger.warning(f"Permisos insuficientes para obtener conexiones de red: {e}")
                net_connections_list = []
            except Exception as e:
                logger.error(f"Error obteniendo conexiones de red: {e}")
                net_connections_list = []
            
            for conn in net_connections_list:
                try:
                    try:
                        if conn.family:
                            family_val = conn.family.value if hasattr(conn.family, 'value') else int(conn.family)
                        else:
                            family_val = 0
                    except (AttributeError, TypeError, ValueError) as e:
                        logger.debug(f"Error obteniendo family de conexión: {e}")
                        family_val = 0
                    
                    try:
                        if conn.type:
                            type_val = conn.type.value if hasattr(conn.type, 'value') else int(conn.type)
                        else:
                            type_val = 0
                    except (AttributeError, TypeError, ValueError) as e:
                        logger.debug(f"Error obteniendo type de conexión: {e}")
                        type_val = 0
                    
                    connection_data = {
                        "fd": conn.fd if conn.fd else -1,
                        "family": family_val,
                        "type": type_val,
                        "laddr": {
                            "ip": str(conn.laddr.ip) if conn.laddr else "0.0.0.0",
                            "port": int(conn.laddr.port) if conn.laddr else 0
                        },
                        "status": str(conn.status) if conn.status else "UNKNOWN",
                        "pid": int(conn.pid) if conn.pid else None
                    }
                    
                    if conn.raddr:
                        try:
                            connection_data["raddr"] = {
                                "ip": str(conn.raddr.ip),
                                "port": int(conn.raddr.port)
                            }
                        except (AttributeError, ValueError) as e:
                            logger.debug(f"Error obteniendo raddr de conexión: {e}")
                            connection_data["raddr"] = None
                    else:
                        connection_data["raddr"] = None
                    
                    connections.append(connection_data)
                    
                    if conn.status and str(conn.status) == "ESTABLISHED":
                        active_connections += 1
                        
                except Exception as e:
                    logger.warning(f"Error procesando conexión: {e}", exc_info=True)
                    continue
            
            timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            
            return jsonify({
                "interfaces": interfaces,
                "connections": connections,
                "total_bytes_sent": total_bytes_sent,
                "total_bytes_recv": total_bytes_recv,
                "total_packets_sent": total_packets_sent,
                "total_packets_recv": total_packets_recv,
                "active_connections": active_connections,
                "timestamp": timestamp
            }), 200
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas de red: {e}", exc_info=True)
            return jsonify({
                "error": "Error interno del servidor",
                "message": str(e)
            }), 500
    
    @bp.route('/network/interfaces/', methods=['GET'], strict_slashes=False)
    @bp.route('/network/interfaces', methods=['GET'], strict_slashes=False)
    @jwt_required()
    def get_network_interfaces():
        """
        Obtiene solo la lista de interfaces de red con sus estadísticas.
        
        Returns:
            JSON con array de interfaces de red
        """
        if not PSUTIL_AVAILABLE:
            return jsonify({
                'error': 'psutil no disponible',
                'message': 'La librería psutil no está instalada. Instalar con: pip install psutil>=5.9.0'
            }), 503
        
        try:
            interfaces = []
            
            try:
                net_io = psutil.net_io_counters(pernic=True)
                net_if_stats = psutil.net_if_stats()
            except Exception as e:
                logger.error(f"Error obteniendo estadísticas de interfaces: {e}")
                return jsonify({
                    'error': 'Error obteniendo interfaces de red',
                    'message': str(e)
                }), 500
            
            for interface_name, stats in net_io.items():
                if_stats = net_if_stats.get(interface_name, {})
                
                interfaces.append({
                    "name": interface_name,
                    "bytes_sent": stats.bytes_sent,
                    "bytes_recv": stats.bytes_recv,
                    "packets_sent": stats.packets_sent,
                    "packets_recv": stats.packets_recv,
                    "errin": stats.errin,
                    "errout": stats.errout,
                    "dropin": stats.dropin,
                    "dropout": stats.dropout,
                    "is_up": if_stats.get("isup", False) if if_stats else False
                })
            
            return jsonify({
                "interfaces": interfaces,
                "count": len(interfaces),
                "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }), 200
            
        except Exception as e:
            logger.error(f"Error obteniendo interfaces de red: {e}", exc_info=True)
            return jsonify({
                "error": "Error interno del servidor",
                "message": str(e)
            }), 500
    
    @bp.route('/network/connections/', methods=['GET'], strict_slashes=False)
    @bp.route('/network/connections', methods=['GET'], strict_slashes=False)
    @jwt_required()
    def get_network_connections():
        """
        Obtiene solo la lista de conexiones de red activas.
        
        Returns:
            JSON con array de conexiones de red
        """
        if not PSUTIL_AVAILABLE:
            return jsonify({
                'error': 'psutil no disponible',
                'message': 'La librería psutil no está instalada. Instalar con: pip install psutil>=5.9.0'
            }), 503
        
        try:
            connections = []
            active_connections = 0
            
            try:
                net_connections_list = psutil.net_connections(kind='inet')
            except (psutil.AccessDenied, PermissionError) as e:
                logger.warning(f"Permisos insuficientes para obtener conexiones de red: {e}")
                return jsonify({
                    "connections": [],
                    "count": 0,
                    "active_connections": 0,
                    "warning": "Permisos insuficientes para obtener conexiones de red",
                    "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }), 200
            except Exception as e:
                logger.error(f"Error obteniendo conexiones de red: {e}")
                return jsonify({
                    "error": "Error obteniendo conexiones de red",
                    "message": str(e)
                }), 500
            
            for conn in net_connections_list:
                try:
                    connection_data = {
                        "fd": conn.fd if conn.fd else -1,
                        "family": conn.family.value if conn.family else 0,
                        "type": conn.type.value if conn.type else 0,
                        "laddr": {
                            "ip": conn.laddr.ip if conn.laddr else "0.0.0.0",
                            "port": conn.laddr.port if conn.laddr else 0
                        },
                        "status": conn.status if conn.status else "UNKNOWN",
                        "pid": conn.pid if conn.pid else None
                    }
                    
                    if conn.raddr:
                        connection_data["raddr"] = {
                            "ip": conn.raddr.ip,
                            "port": conn.raddr.port
                        }
                    else:
                        connection_data["raddr"] = None
                    
                    connections.append(connection_data)
                    
                    if conn.status == "ESTABLISHED":
                        active_connections += 1
                        
                except Exception as e:
                    logger.warning(f"Error procesando conexión: {e}")
                    continue
            
            return jsonify({
                "connections": connections,
                "count": len(connections),
                "active_connections": active_connections,
                "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }), 200
            
        except Exception as e:
            logger.error(f"Error obteniendo conexiones de red: {e}", exc_info=True)
            return jsonify({
                "error": "Error interno del servidor",
                "message": str(e)
            }), 500


