"""
SMB Enumeration Routes
======================

Rutas para enumeración SMB/CIFS.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ScanningService

logger = logging.getLogger(__name__)

scanning_service = ScanningService()


def register_routes(bp: Blueprint):
    """Registra las rutas de enumeración SMB en el blueprint."""
    
    @bp.route('/enum/smb/enum4linux', methods=['POST'])
    @jwt_required()
    def enum4linux_scan():
        """Enumeración SMB con enum4linux."""
        try:
            data = request.get_json()
            logger.info(f"[enum4linux] Request data: {data}")
            
            target = data.get('target')
            workspace_id = data.get('workspace_id')
            current_user_id = get_jwt_identity()
            
            if not target or not workspace_id:
                return jsonify({'error': 'target and workspace_id required'}), 400
            
            result = scanning_service.start_enum4linux(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                use_ng=data.get('use_ng', True),
                all=data.get('all', False)
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"[enum4linux] Error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/enum/smb/smbmap', methods=['POST'])
    @jwt_required()
    def smbmap_scan():
        """Enumeración SMB con smbmap."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        current_user_id = get_jwt_identity()
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            result = scanning_service.start_smbmap(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                username=data.get('username'),
                password=data.get('password'),
                share=data.get('share')
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error in smbmap: {e}")
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/enum/smb/smbclient', methods=['POST'])
    @jwt_required()
    def smbclient_scan():
        """Enumeración SMB con smbclient."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        current_user_id = get_jwt_identity()
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            result = scanning_service.start_smbclient(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                share=data.get('share', 'IPC$'),
                username=data.get('username'),
                password=data.get('password')
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error in smbclient: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500


