"""
Scan Management Routes
======================

Rutas para gestión de escaneos.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ScanningService
from models import Scan

logger = logging.getLogger(__name__)

scanning_service = ScanningService()


def register_routes(bp: Blueprint):
    """Registra las rutas de gestión de scans en el blueprint."""
    
    @bp.route('/start', methods=['POST'])
    @jwt_required()
    def start_scan():
        """Endpoint unificado para iniciar escaneos."""
        data = request.get_json() or {}
        current_user_id = get_jwt_identity()
        
        logger.info(f"📡 POST /scanning/start - User: {current_user_id}, Data: {data}")
        
        target = data.get('target')
        workspace_id = data.get('workspace_id') or request.args.get('workspace_id', type=int)
        
        if not target:
            return jsonify({'error': 'Target is required'}), 400
        
        if not workspace_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        
        scan_type = data.get('scan_type', 'comprehensive')
        tool = data.get('tool', 'nmap')
        ports = data.get('ports')
        
        valid_tools = ['nmap', 'masscan', 'rustscan']
        if tool not in valid_tools:
            return jsonify({'error': f'Invalid tool. Must be one of: {valid_tools}'}), 400
        
        scan_type_map = {
            'vulnerability': 'vuln',
            'network': 'discovery'
        }
        
        if scan_type in scan_type_map:
            scan_type = scan_type_map[scan_type]
        
        valid_types = ['comprehensive', 'quick', 'stealth', 'vuln', 'discovery', 'udp', 'detailed', 'custom', 'service', 'os']
        if scan_type not in valid_types:
            return jsonify({'error': f'Invalid scan_type. Must be one of: {valid_types}'}), 400
        
        try:
            if tool == 'nmap':
                result = scanning_service.start_nmap_scan(
                    target=target,
                    scan_type=scan_type,
                    workspace_id=workspace_id,
                    user_id=current_user_id,
                    ports=ports
                )
            elif tool == 'rustscan':
                result = scanning_service.start_rustscan(
                    target=target,
                    workspace_id=workspace_id,
                    user_id=current_user_id,
                    batch_size=data.get('batch_size', 4000),
                    timeout=data.get('timeout', 1500),
                    ulimit=data.get('ulimit', 5000)
                )
            elif tool == 'masscan':
                result = scanning_service.start_masscan(
                    target=target,
                    ports=ports or '1-65535',
                    workspace_id=workspace_id,
                    user_id=current_user_id,
                    rate=data.get('rate', 1000),
                    environment=data.get('environment', 'internal')
                )
            
            return jsonify(result), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in start_scan: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/scans', methods=['GET'])
    @jwt_required()
    def list_scans():
        """Lista todos los escaneos del usuario."""
        current_user_id = get_jwt_identity()
        
        workspace_id = request.args.get('workspace_id', type=int)
        status = request.args.get('status')
        
        query = Scan.query.filter_by(user_id=current_user_id)
        
        if workspace_id:
            query = query.filter_by(workspace_id=workspace_id)
        
        if status:
            query = query.filter_by(status=status)
        
        scans = query.order_by(Scan.created_at.desc()).all()
        
        return jsonify({
            'scans': [{
                'id': scan.id,
                'scan_type': scan.scan_type,
                'target': scan.target,
                'status': scan.status,
                'progress': scan.progress,
                'options': scan.options,  # Incluir options para identificar herramientas
                'started_at': scan.started_at.isoformat() if scan.started_at else None,
                'completed_at': scan.completed_at.isoformat() if scan.completed_at else None,
                'created_at': scan.created_at.isoformat() if scan.created_at else None
            } for scan in scans],
            'total': len(scans)
        }), 200
    
    @bp.route('/sessions', methods=['GET', 'OPTIONS'])
    def get_scan_sessions():
        """Lista sesiones de escaneo activas (alias para /scans)."""
        if request.method == 'OPTIONS':
            return '', 204
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request()
        # Llamar a list_scans directamente
        current_user_id = get_jwt_identity()
        workspace_id = request.args.get('workspace_id', type=int)
        status = request.args.get('status')
        
        query = Scan.query.filter_by(user_id=current_user_id)
        
        if workspace_id:
            query = query.filter_by(workspace_id=workspace_id)
        
        if status:
            query = query.filter_by(status=status)
        
        scans = query.order_by(Scan.created_at.desc()).all()
        
        return jsonify({
            'scans': [{
                'id': scan.id,
                'scan_type': scan.scan_type,
                'target': scan.target,
                'status': scan.status,
                'progress': scan.progress,
                'options': scan.options,  # Incluir options para identificar herramientas
                'started_at': scan.started_at.isoformat() if scan.started_at else None,
                'completed_at': scan.completed_at.isoformat() if scan.completed_at else None,
                'created_at': scan.created_at.isoformat() if scan.created_at else None
            } for scan in scans],
            'total': len(scans)
        }), 200
    
    @bp.route('/scans/<int:scan_id>', methods=['GET'])
    @jwt_required()
    def get_scan(scan_id):
        """Obtiene detalles de un escaneo."""
        try:
            result = scanning_service.get_scan_status(scan_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            logger.error(f"Error in get_scan endpoint: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/scans/<int:scan_id>/results', methods=['GET'])
    @jwt_required()
    def get_scan_results(scan_id):
        """Obtiene resultados parseados de un escaneo."""
        try:
            # Intentar usar get_scan_results si existe, sino usar parse_nmap_results
            if hasattr(scanning_service, 'get_scan_results'):
                result = scanning_service.get_scan_results(scan_id)
            else:
                result = scanning_service.parse_nmap_results(scan_id)
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Error parsing results: {e}")
            return jsonify({'error': 'Error parsing results'}), 500

