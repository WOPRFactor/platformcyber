"""
Network Services Enumeration Routes
===================================

Rutas para enumeración de servicios de red.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ScanningService

logger = logging.getLogger(__name__)

scanning_service = ScanningService()


def register_routes(bp: Blueprint):
    """Registra las rutas de enumeración de servicios de red en el blueprint."""
    
    @bp.route('/enum/ssh', methods=['POST'])
    @jwt_required()
    def ssh_enum():
        """Enumeración SSH."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        current_user_id = get_jwt_identity()
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            result = scanning_service.start_ssh_enum(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                port=data.get('port', 22),
                tool=data.get('tool', 'nmap')
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error in SSH enum: {e}")
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/enum/ftp', methods=['POST'])
    @jwt_required()
    def ftp_enum():
        """Enumeración FTP."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        current_user_id = get_jwt_identity()
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            port = data.get('port', 21)
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.start_ftp_enum(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                port=port
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error in FTP enum: {e}")
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/enum/smtp', methods=['POST'])
    @jwt_required()
    def smtp_enum():
        """Enumeración SMTP."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        current_user_id = get_jwt_identity()
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            result = scanning_service.start_smtp_enum(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                port=data.get('port', 25),
                tool=data.get('tool', 'nmap')
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error in SMTP enum: {e}")
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/enum/dns', methods=['POST'])
    @jwt_required()
    def dns_enum():
        """Enumeración DNS."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        current_user_id = get_jwt_identity()
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            port = data.get('port', 53)
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.start_dns_enum(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                domain=data.get('domain'),
                port=port,
                tool=data.get('tool', 'nmap')
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error in DNS enum: {e}")
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/enum/snmp', methods=['POST'])
    @jwt_required()
    def snmp_enum():
        """Enumeración SNMP."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        current_user_id = get_jwt_identity()
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            result = scanning_service.start_snmp_enum(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                port=data.get('port', 161),
                community=data.get('community', 'public')
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error in SNMP enum: {e}")
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/enum/ldap', methods=['POST'])
    @jwt_required()
    def ldap_enum():
        """Enumeración LDAP."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        current_user_id = get_jwt_identity()
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            result = scanning_service.start_ldap_enum(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                port=data.get('port', 389),
                tool=data.get('tool', 'nmap')
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error in LDAP enum: {e}")
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/enum/rdp', methods=['POST'])
    @jwt_required()
    def rdp_enum():
        """Enumeración RDP."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        current_user_id = get_jwt_identity()
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            port = data.get('port', 3389)
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.start_rdp_enum(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                port=port
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error in RDP enum: {e}")
            return jsonify({'error': str(e)}), 500


