"""
DNS Enumeration Routes
======================

Endpoints para enumeración y consultas DNS.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ReconnaissanceService

logger = logging.getLogger(__name__)

# Crear sub-blueprint
dns_bp = Blueprint('dns', __name__)

# Inicializar servicio
recon_service = ReconnaissanceService()


@dns_bp.route('/dns/preview', methods=['POST'])
@jwt_required()
def preview_dns_recon():
    """Preview del comando DNS recon."""
    data = request.get_json()
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    record_types = data.get('record_types')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_dns_recon(
            domain=domain,
            workspace_id=workspace_id,
            record_types=record_types
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_dns_recon: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@dns_bp.route('/dns', methods=['POST'])
@jwt_required()
def dns_recon():
    """
    Enumeración DNS con DNSRecon.
    
    Body:
        {
            "domain": "example.com",
            "workspace_id": 1,
            "record_types": ["A", "AAAA", "MX", "NS", "TXT"] (opcional)
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    record_types = data.get('record_types')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_dns_recon(
            domain=domain,
            workspace_id=workspace_id,
            user_id=current_user_id,
            record_types=record_types
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in dns_recon: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@dns_bp.route('/dns-lookup/preview', methods=['POST'])
@jwt_required()
def preview_dns_lookup():
    """Preview del comando DNS lookup."""
    data = request.get_json()
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    tool = data.get('tool', 'host')
    record_type = data.get('record_type')
    dns_server = data.get('dns_server')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_dns_lookup(
            domain=domain,
            workspace_id=workspace_id,
            tool=tool,
            record_type=record_type,
            dns_server=dns_server
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_dns_lookup: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@dns_bp.route('/dns-lookup', methods=['POST'])
@jwt_required()
def dns_lookup():
    """
    Consultas DNS simples con host o nslookup.
    
    Body:
        {
            "domain": "example.com",
            "workspace_id": 1,
            "tool": "host|nslookup" (opcional, default: host),
            "record_type": "A|MX|NS|TXT|SOA" (opcional),
            "dns_server": "8.8.8.8" (opcional)
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    tool = data.get('tool', 'host')
    record_type = data.get('record_type')
    dns_server = data.get('dns_server')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_dns_lookup(
            domain=domain,
            workspace_id=workspace_id,
            user_id=current_user_id,
            tool=tool,
            record_type=record_type,
            dns_server=dns_server
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        logger.error(f"ValueError in dns_lookup: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in dns_lookup: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@dns_bp.route('/dns-enum-alt/preview', methods=['POST'])
@jwt_required()
def preview_dns_enum_alt():
    """Preview del comando DNS enum alt."""
    data = request.get_json()
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    tool = data.get('tool', 'dnsenum')
    wordlist = data.get('wordlist')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.preview_dns_enum_alt(
            domain=domain,
            workspace_id=workspace_id,
            tool=tool,
            wordlist=wordlist
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_dns_enum_alt: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@dns_bp.route('/dns-enum-alt', methods=['POST'])
@jwt_required()
def dns_enum_alt():
    """
    Enumeración DNS alternativa con dnsenum o fierce.
    
    Body:
        {
            "domain": "example.com",
            "workspace_id": 1,
            "tool": "dnsenum" | "fierce" (default: "dnsenum"),
            "wordlist": "path/to/wordlist.txt" (opcional)
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    tool = data.get('tool', 'dnsenum')
    wordlist = data.get('wordlist')
    
    if not domain or not workspace_id:
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_dns_enum_alt(
            domain=domain,
            workspace_id=workspace_id,
            user_id=current_user_id,
            tool=tool,
            wordlist=wordlist
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        logger.error(f"ValueError in dns_enum_alt: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in dns_enum_alt: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@dns_bp.route('/traceroute/preview', methods=['POST'])
@jwt_required()
def preview_traceroute():
    """Preview del comando traceroute."""
    data = request.get_json()
    target = data.get('target')
    workspace_id = data.get('workspace_id')
    protocol = data.get('protocol', 'icmp')
    max_hops = data.get('max_hops', 30)
    
    if not target or not workspace_id:
        return jsonify({'error': 'target and workspace_id are required'}), 400
    
    try:
        # Asegurar que max_hops sea un entero válido
        if isinstance(max_hops, (int, float)):
            max_hops = int(max_hops)
        elif isinstance(max_hops, str):
            try:
                max_hops = int(max_hops)
            except ValueError:
                max_hops = 30
        else:
            max_hops = 30
        
        if max_hops < 1 or max_hops > 255:
            max_hops = 30
        
        result = recon_service.preview_traceroute(
            target=target,
            workspace_id=workspace_id,
            protocol=protocol,
            max_hops=max_hops
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in preview_traceroute: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@dns_bp.route('/traceroute', methods=['POST'])
@jwt_required()
def traceroute_scan():
    """
    Mapeo de ruta de red con traceroute.
    
    Body:
        {
            "target": "192.168.1.1",
            "workspace_id": 1,
            "protocol": "icmp|tcp|udp" (opcional, default: icmp),
            "max_hops": 30 (opcional, default: 30)
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    logger.info(f"Traceroute request data: {data}")
    
    target = data.get('target')
    workspace_id = data.get('workspace_id')
    protocol = data.get('protocol', 'icmp')
    max_hops = data.get('max_hops', 30)
    
    # Asegurar que max_hops sea un entero
    # Si es un diccionario u otro tipo, usar el valor por defecto
    if isinstance(max_hops, dict):
        logger.warning(f"max_hops is a dict: {max_hops}, using default 30")
        max_hops = 30
    elif isinstance(max_hops, (int, float)):
        max_hops = int(max_hops)
    elif isinstance(max_hops, str):
        try:
            max_hops = int(max_hops)
        except ValueError:
            logger.warning(f"Invalid max_hops string: {max_hops}, using default 30")
            max_hops = 30
    else:
        logger.warning(f"Invalid max_hops type: {type(max_hops)}, value: {max_hops}, using default 30")
        max_hops = 30
    
    # Validar que max_hops esté en un rango razonable
    if max_hops < 1 or max_hops > 255:
        logger.warning(f"max_hops out of range: {max_hops}, clamping to 30")
        max_hops = 30
    
    if not target or not workspace_id:
        return jsonify({'error': 'target and workspace_id are required'}), 400
    
    try:
        result = recon_service.start_traceroute(
            target=target,
            workspace_id=workspace_id,
            user_id=current_user_id,
            protocol=protocol,
            max_hops=max_hops
        )
        
        return jsonify(result), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in traceroute_scan: {e}")
        return jsonify({'error': 'Internal server error'}), 500


