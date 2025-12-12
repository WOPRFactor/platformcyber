"""
Integrations API
================

Endpoints para integraciones avanzadas:
- Metasploit Framework
- Burp Suite Professional
- Nmap Advanced
- SQLMap
- Gobuster
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services.integrations import IntegrationsService

logger = logging.getLogger(__name__)

integrations_bp = Blueprint('integrations', __name__)
integrations_service = IntegrationsService()


# ============================================================================
# METASPLOIT
# ============================================================================

@integrations_bp.route('/metasploit/status', methods=['GET'])
@jwt_required()
def metasploit_status():
    """Verifica el estado de la conexión con Metasploit."""
    try:
        result = integrations_service.check_metasploit_status()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error checking Metasploit status: {e}")
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/metasploit/modules', methods=['GET'])
@jwt_required()
def metasploit_modules():
    """Lista módulos de Metasploit."""
    try:
        module_type = request.args.get('type')
        result = integrations_service.list_metasploit_modules(module_type)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error listing Metasploit modules: {e}")
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/metasploit/exploit', methods=['POST'])
@jwt_required()
def metasploit_exploit():
    """Ejecuta un exploit de Metasploit."""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        exploit = data.get('exploit')
        options = data.get('options', {})
        workspace_id = data.get('workspace_id')
        
        if not exploit:
            return jsonify({'error': 'exploit is required'}), 400
        if not workspace_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        
        result = integrations_service.execute_metasploit_exploit(
            exploit=exploit,
            options=options,
            workspace_id=workspace_id,
            user_id=current_user_id
        )
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error executing Metasploit exploit: {e}")
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/metasploit/sessions', methods=['GET'])
@jwt_required()
def metasploit_sessions():
    """Lista sesiones activas de Metasploit."""
    try:
        result = integrations_service.get_metasploit_sessions()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error listing Metasploit sessions: {e}")
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/metasploit/sessions/<session_id>/interact', methods=['POST'])
@jwt_required()
def metasploit_session_interact(session_id: str):
    """Interactúa con una sesión de Metasploit."""
    try:
        data = request.get_json()
        command = data.get('command')
        
        if not command:
            return jsonify({'error': 'command is required'}), 400
        
        # TODO: Implementar interacción real con sesiones de Metasploit
        # Esto requiere msfrpcd o acceso directo a la consola
        return jsonify({
            'success': False,
            'message': 'Session interaction requires msfrpcd configuration',
            'session_id': session_id,
            'command': command
        }), 501
    except Exception as e:
        logger.error(f"Error interacting with Metasploit session: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# BURP SUITE
# ============================================================================

@integrations_bp.route('/burp/status', methods=['GET'])
@jwt_required()
def burp_status():
    """Verifica el estado de la conexión con Burp Suite."""
    try:
        result = integrations_service.check_burp_status()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error checking Burp status: {e}")
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/burp/scan', methods=['POST'])
@jwt_required()
def burp_scan():
    """Inicia un scan de Burp Suite."""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        url = data.get('url')
        workspace_id = data.get('workspace_id')
        
        if not url:
            return jsonify({'error': 'url is required'}), 400
        if not workspace_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        
        result = integrations_service.start_burp_scan(
            url=url,
            workspace_id=workspace_id,
            user_id=current_user_id
        )
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error starting Burp scan: {e}")
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/burp/scan/<scan_id>/status', methods=['GET'])
@jwt_required()
def burp_scan_status(scan_id: str):
    """Obtiene el estado de un scan de Burp."""
    try:
        session_details = integrations_service.get_session_details(int(scan_id))
        return jsonify({
            'scan_id': scan_id,
            'status': session_details.get('status', 'unknown')
        }), 200
    except Exception as e:
        logger.error(f"Error getting Burp scan status: {e}")
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/burp/scan/<scan_id>/results', methods=['GET'])
@jwt_required()
def burp_scan_results(scan_id: str):
    """Obtiene los resultados de un scan de Burp."""
    try:
        session_details = integrations_service.get_session_details(int(scan_id))
        return jsonify({
            'scan_id': scan_id,
            'results': session_details,
            'message': 'Burp Suite results require API configuration'
        }), 200
    except Exception as e:
        logger.error(f"Error getting Burp scan results: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# NMAP ADVANCED
# ============================================================================

@integrations_bp.route('/nmap/advanced', methods=['POST'])
@jwt_required()
def nmap_advanced():
    """Ejecuta un scan avanzado de Nmap."""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        target = data.get('target')
        options = data.get('options', {})
        workspace_id = data.get('workspace_id')
        
        if not target:
            return jsonify({'error': 'target is required'}), 400
        if not workspace_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        
        result = integrations_service.advanced_nmap_scan(
            target=target,
            options=options,
            workspace_id=workspace_id,
            user_id=current_user_id
        )
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error executing advanced Nmap scan: {e}")
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/nmap/results/<session_id>', methods=['GET'])
@jwt_required()
def nmap_results(session_id: str):
    """Obtiene resultados de un scan de Nmap."""
    try:
        result = integrations_service.get_nmap_results(int(session_id))
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting Nmap results: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SQLMAP
# ============================================================================

@integrations_bp.route('/sqlmap/scan', methods=['POST'])
@jwt_required()
def sqlmap_scan():
    """Ejecuta un scan de SQLMap."""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        url = data.get('url')
        options = data.get('options', {})
        workspace_id = data.get('workspace_id')
        
        if not url:
            return jsonify({'error': 'url is required'}), 400
        if not workspace_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        
        result = integrations_service.sqlmap_scan(
            url=url,
            options=options,
            workspace_id=workspace_id,
            user_id=current_user_id
        )
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error executing SQLMap scan: {e}")
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/sqlmap/results/<session_id>', methods=['GET'])
@jwt_required()
def sqlmap_results(session_id: str):
    """Obtiene resultados de un scan de SQLMap."""
    try:
        result = integrations_service.get_sqlmap_results(int(session_id))
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting SQLMap results: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# GOBUSTER
# ============================================================================

@integrations_bp.route('/gobuster/directory', methods=['POST'])
@jwt_required()
def gobuster_directory():
    """Ejecuta directory busting con Gobuster."""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        url = data.get('url')
        wordlist = data.get('wordlist', '/usr/share/wordlists/dirb/common.txt')
        options = data.get('options', {})
        workspace_id = data.get('workspace_id')
        
        if not url:
            return jsonify({'error': 'url is required'}), 400
        if not workspace_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        
        result = integrations_service.gobuster_directory(
            url=url,
            wordlist=wordlist,
            options=options,
            workspace_id=workspace_id,
            user_id=current_user_id
        )
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error executing Gobuster directory busting: {e}")
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/gobuster/results/<session_id>', methods=['GET'])
@jwt_required()
def gobuster_results(session_id: str):
    """Obtiene resultados de Gobuster."""
    try:
        result = integrations_service.get_gobuster_results(int(session_id))
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting Gobuster results: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SESSIONS
# ============================================================================

@integrations_bp.route('/sessions', methods=['GET'])
@jwt_required()
def integration_sessions():
    """Lista todas las sesiones de integraciones."""
    try:
        workspace_id = request.args.get('workspace_id', type=int)
        sessions = integrations_service.get_integration_sessions(workspace_id=workspace_id)
        return jsonify({'sessions': sessions}), 200
    except Exception as e:
        logger.error(f"Error listing integration sessions: {e}")
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/sessions/<session_id>', methods=['GET'])
@jwt_required()
def session_details(session_id: str):
    """Obtiene detalles de una sesión de integración."""
    try:
        details = integrations_service.get_session_details(int(session_id))
        return jsonify(details), 200
    except Exception as e:
        logger.error(f"Error getting session details: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PREVIEW ENDPOINTS
# ============================================================================

@integrations_bp.route('/metasploit/exploit/preview', methods=['POST'])
@jwt_required()
def preview_metasploit_exploit():
    """Preview del comando Metasploit."""
    try:
        data = request.get_json()
        exploit = data.get('exploit')
        options = data.get('options', {})
        workspace_id = data.get('workspace_id')
        
        if not exploit:
            return jsonify({'error': 'exploit is required'}), 400
        if not workspace_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        
        result = integrations_service.preview_metasploit_exploit(
            exploit=exploit,
            options=options,
            workspace_id=workspace_id
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_metasploit_exploit: {e}")
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/burp/scan/preview', methods=['POST'])
@jwt_required()
def preview_burp_scan():
    """Preview del comando Burp Suite."""
    try:
        data = request.get_json()
        url = data.get('url')
        workspace_id = data.get('workspace_id')
        
        if not url:
            return jsonify({'error': 'url is required'}), 400
        if not workspace_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        
        result = integrations_service.preview_burp_scan(
            url=url,
            workspace_id=workspace_id
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_burp_scan: {e}")
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/nmap/advanced/preview', methods=['POST'])
@jwt_required()
def preview_nmap_scan():
    """Preview del comando Nmap avanzado."""
    try:
        data = request.get_json()
        target = data.get('target')
        options = data.get('options', {})
        workspace_id = data.get('workspace_id')
        
        if not target:
            return jsonify({'error': 'target is required'}), 400
        if not workspace_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        
        result = integrations_service.preview_nmap_scan(
            target=target,
            options=options,
            workspace_id=workspace_id
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_nmap_scan: {e}")
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/sqlmap/scan/preview', methods=['POST'])
@jwt_required()
def preview_sqlmap_scan():
    """Preview del comando SQLMap."""
    try:
        data = request.get_json()
        url = data.get('url')
        options = data.get('options', {})
        workspace_id = data.get('workspace_id')
        
        if not url:
            return jsonify({'error': 'url is required'}), 400
        if not workspace_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        
        result = integrations_service.preview_sqlmap_scan(
            url=url,
            options=options,
            workspace_id=workspace_id
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_sqlmap_scan: {e}")
        return jsonify({'error': str(e)}), 500


@integrations_bp.route('/gobuster/directory/preview', methods=['POST'])
@jwt_required()
def preview_gobuster_directory():
    """Preview del comando Gobuster."""
    try:
        data = request.get_json()
        url = data.get('url')
        wordlist = data.get('wordlist', '/usr/share/wordlists/dirb/common.txt')
        options = data.get('options', {})
        workspace_id = data.get('workspace_id')
        
        if not url:
            return jsonify({'error': 'url is required'}), 400
        if not workspace_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        
        result = integrations_service.preview_gobuster_directory(
            url=url,
            wordlist=wordlist,
            options=options,
            workspace_id=workspace_id
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_gobuster_directory: {e}")
        return jsonify({'error': str(e)}), 500


