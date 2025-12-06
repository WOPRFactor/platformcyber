"""
Impacket API Endpoints
======================

Endpoints REST para Impacket Suite.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.impacket_service import ImpacketService
from repositories import ScanRepository
import logging

logger = logging.getLogger(__name__)

impacket_bp = Blueprint('impacket', __name__)
impacket_service = ImpacketService()
scan_repo = ScanRepository()


@impacket_bp.route('/psexec', methods=['POST'])
@jwt_required()
def psexec():
    """Ejecuta psexec.py para ejecución remota."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        required = ['target', 'username', 'workspace_id']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing {field}'}), 400
        
        if 'password' not in data and 'hash' not in data:
            return jsonify({'error': 'Must provide password or hash'}), 400
        
        # Crear scan
        scan = scan_repo.create(
            scan_type='post_exploitation',
            target=data['target'],
            workspace_id=data['workspace_id'],
            user_id=user_id,
            options={'tool': 'psexec', **data.get('options', {})}
        )
        
        # Ejecutar
        result = impacket_service.psexec(
            target=data['target'],
            username=data['username'],
            password=data.get('password'),
            hash=data.get('hash'),
            domain=data.get('domain'),
            command=data.get('command', 'whoami'),
            options=data.get('options', {})
        )
        
        # Actualizar scan
        if result['status'] == 'completed':
            scan_repo.update_status(scan, 'completed')
        else:
            scan_repo.update_status(scan, 'failed')
        
        return jsonify({
            'scan_id': scan.id,
            **result
        }), 201
    
    except Exception as e:
        logger.error(f"Error in psexec: {e}")
        return jsonify({'error': str(e)}), 500


@impacket_bp.route('/secretsdump', methods=['POST'])
@jwt_required()
def secretsdump():
    """Ejecuta secretsdump.py para extraer secretos."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        required = ['target', 'username', 'workspace_id']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing {field}'}), 400
        
        if 'password' not in data and 'hash' not in data:
            return jsonify({'error': 'Must provide password or hash'}), 400
        
        # Crear scan
        scan = scan_repo.create(
            scan_type='post_exploitation',
            target=data['target'],
            workspace_id=data['workspace_id'],
            user_id=user_id,
            options={'tool': 'secretsdump', **data.get('options', {})}
        )
        
        # Ejecutar
        result = impacket_service.secretsdump(
            target=data['target'],
            username=data['username'],
            password=data.get('password'),
            hash=data.get('hash'),
            domain=data.get('domain'),
            options=data.get('options', {})
        )
        
        # Actualizar scan
        if result['status'] == 'completed':
            scan_repo.update_status(scan, 'completed')
        else:
            scan_repo.update_status(scan, 'failed')
        
        return jsonify({
            'scan_id': scan.id,
            **result
        }), 201
    
    except Exception as e:
        logger.error(f"Error in secretsdump: {e}")
        return jsonify({'error': str(e)}), 500


@impacket_bp.route('/get-user-spns', methods=['POST'])
@jwt_required()
def get_user_spns():
    """Ejecuta GetUserSPNs.py (Kerberoasting)."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        required = ['target', 'username', 'workspace_id']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing {field}'}), 400
        
        if 'password' not in data and 'hash' not in data:
            return jsonify({'error': 'Must provide password or hash'}), 400
        
        # Crear scan
        scan = scan_repo.create(
            scan_type='active_directory',
            target=data['target'],
            workspace_id=data['workspace_id'],
            user_id=user_id,
            options={'tool': 'GetUserSPNs', **data.get('options', {})}
        )
        
        # Ejecutar
        result = impacket_service.get_user_spns(
            target=data['target'],
            username=data['username'],
            password=data.get('password'),
            hash=data.get('hash'),
            domain=data.get('domain'),
            dc_ip=data.get('dc_ip'),
            options=data.get('options', {})
        )
        
        # Actualizar scan
        if result['status'] == 'completed':
            scan_repo.update_status(scan, 'completed')
        else:
            scan_repo.update_status(scan, 'failed')
        
        return jsonify({
            'scan_id': scan.id,
            **result
        }), 201
    
    except Exception as e:
        logger.error(f"Error in GetUserSPNs: {e}")
        return jsonify({'error': str(e)}), 500


@impacket_bp.route('/get-np-users', methods=['POST'])
@jwt_required()
def get_np_users():
    """Ejecuta GetNPUsers.py (ASREPRoasting)."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        required = ['target', 'workspace_id']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing {field}'}), 400
        
        # Crear scan
        scan = scan_repo.create(
            scan_type='active_directory',
            target=data['target'],
            workspace_id=data['workspace_id'],
            user_id=user_id,
            options={'tool': 'GetNPUsers', **data.get('options', {})}
        )
        
        # Ejecutar
        result = impacket_service.get_np_users(
            target=data['target'],
            username=data.get('username'),
            password=data.get('password'),
            domain=data.get('domain'),
            dc_ip=data.get('dc_ip'),
            usersfile=data.get('usersfile'),
            options=data.get('options', {})
        )
        
        # Actualizar scan
        if result['status'] == 'completed':
            scan_repo.update_status(scan, 'completed')
        else:
            scan_repo.update_status(scan, 'failed')
        
        return jsonify({
            'scan_id': scan.id,
            **result
        }), 201
    
    except Exception as e:
        logger.error(f"Error in GetNPUsers: {e}")
        return jsonify({'error': str(e)}), 500


@impacket_bp.route('/check-installation', methods=['GET'])
@jwt_required()
def check_installation():
    """Verifica si las herramientas de Impacket están instaladas."""
    try:
        status = impacket_service.check_impacket_installed()
        
        return jsonify({
            'tools': status,
            'all_installed': all(status.values())
        }), 200
    
    except Exception as e:
        logger.error(f"Error checking Impacket installation: {e}")
        return jsonify({'error': 'Internal server error'}), 500



