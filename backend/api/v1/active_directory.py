"""
Active Directory API Endpoints
===============================

Endpoints para operaciones de pentesting en Active Directory.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ActiveDirectoryService

logger = logging.getLogger(__name__)

active_directory_bp = Blueprint('active_directory', __name__)

# Inicializar servicio
ad_service = ActiveDirectoryService()


@active_directory_bp.route('/kerbrute/userenum', methods=['POST'])
@jwt_required()
def kerbrute_user_enum():
    """
    Enumera usuarios válidos con Kerbrute.
    
    Body:
        {
            "domain": "domain.com",
            "dc_ip": "192.168.1.10",
            "userlist": "/path/to/users.txt",
            "workspace_id": 1
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    domain = data.get('domain')
    dc_ip = data.get('dc_ip')
    userlist = data.get('userlist')
    workspace_id = data.get('workspace_id')
    
    if not all([domain, dc_ip, userlist, workspace_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        result = ad_service.start_kerbrute_userenum(
            domain=domain,
            dc_ip=dc_ip,
            userlist=userlist,
            workspace_id=workspace_id,
            user_id=int(current_user_id)
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in kerbrute_user_enum: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@active_directory_bp.route('/kerbrute/passwordspray', methods=['POST'])
@jwt_required()
def kerbrute_password_spray():
    """
    Password spraying con Kerbrute.
    
    Body:
        {
            "domain": "domain.com",
            "dc_ip": "192.168.1.10",
            "userlist": "/path/to/users.txt",
            "password": "Password123!",
            "workspace_id": 1
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    domain = data.get('domain')
    dc_ip = data.get('dc_ip')
    userlist = data.get('userlist')
    password = data.get('password')
    workspace_id = data.get('workspace_id')
    
    if not all([domain, dc_ip, userlist, password, workspace_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        result = ad_service.start_kerbrute_passwordspray(
            domain=domain,
            dc_ip=dc_ip,
            userlist=userlist,
            password=password,
            workspace_id=workspace_id,
            user_id=int(current_user_id)
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in kerbrute_password_spray: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@active_directory_bp.route('/asreproast', methods=['POST'])
@jwt_required()
def asrep_roast():
    """
    AS-REP Roasting con GetNPUsers.py.
    
    Body:
        {
            "domain": "domain.com",
            "workspace_id": 1,
            "dc_ip": "192.168.1.10",  // opcional
            "username": "user",       // opcional si no_pass
            "password": "pass",       // opcional si no_pass
            "usersfile": "/path/to/users.txt",  // opcional
            "no_pass": true           // default: true
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    
    if not all([domain, workspace_id]):
        return jsonify({'error': 'Domain and workspace_id are required'}), 400
    
    try:
        result = ad_service.start_getnpusers(
            domain=domain,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            username=data.get('username'),
            password=data.get('password'),
            dc_ip=data.get('dc_ip'),
            usersfile=data.get('usersfile'),
            no_pass=data.get('no_pass', True)
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in asrep_roast: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@active_directory_bp.route('/ldap/dump', methods=['POST'])
@jwt_required()
def ldap_dump():
    """
    LDAP domain dump.
    
    Body:
        {
            "dc_ip": "192.168.1.10",
            "username": "user",
            "password": "pass",
            "domain": "domain.com",
            "workspace_id": 1
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    dc_ip = data.get('dc_ip')
    username = data.get('username')
    password = data.get('password')
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    
    if not all([dc_ip, username, password, domain, workspace_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        result = ad_service.start_ldapdomaindump(
            dc_ip=dc_ip,
            username=username,
            password=password,
            domain=domain,
            workspace_id=workspace_id,
            user_id=int(current_user_id)
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in ldap_dump: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@active_directory_bp.route('/dns/dump', methods=['POST'])
@jwt_required()
def dns_dump():
    """
    AD DNS dump (adidnsdump).
    
    Body:
        {
            "dc_ip": "192.168.1.10",
            "username": "user",
            "password": "pass",
            "domain": "domain.com",
            "workspace_id": 1
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    dc_ip = data.get('dc_ip')
    username = data.get('username')
    password = data.get('password')
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    
    if not all([dc_ip, username, password, domain, workspace_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        result = ad_service.start_adidnsdump(
            dc_ip=dc_ip,
            username=username,
            password=password,
            domain=domain,
            workspace_id=workspace_id,
            user_id=int(current_user_id)
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in dns_dump: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@active_directory_bp.route('/cme/enum/users', methods=['POST'])
@jwt_required()
def cme_enum_users():
    """
    Enumera usuarios con CrackMapExec.
    
    Body:
        {
            "dc_ip": "192.168.1.10",
            "username": "user",
            "password": "pass",
            "domain": "domain.com",
            "workspace_id": 1
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    dc_ip = data.get('dc_ip')
    username = data.get('username')
    password = data.get('password')
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    
    if not all([dc_ip, username, password, domain, workspace_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        result = ad_service.start_cme_enum_users(
            dc_ip=dc_ip,
            username=username,
            password=password,
            domain=domain,
            workspace_id=workspace_id,
            user_id=int(current_user_id)
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in cme_enum_users: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@active_directory_bp.route('/scan/<int:scan_id>/results', methods=['GET'])
@jwt_required()
def get_ad_scan_results(scan_id: int):
    """
    Obtiene resultados de un scan AD.
    """
    try:
        results = ad_service.get_scan_results(scan_id)
        return jsonify(results), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting AD scan results: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@active_directory_bp.route('/scan/<int:scan_id>', methods=['GET'])
@jwt_required()
def get_ad_scan_status(scan_id: int):
    """
    Obtiene estado de un scan AD.
    """
    from repositories import ScanRepository
    scan_repo = ScanRepository()
    
    try:
        scan = scan_repo.find_by_id(scan_id)
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404
        
        return jsonify({
            'scan_id': scan.id,
            'status': scan.status,
            'progress': scan.progress,
            'target': scan.target,
            'tool': scan.options.get('tool'),
            'action': scan.options.get('action'),
            'started_at': scan.started_at.isoformat() if scan.started_at else None,
            'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
        }), 200
    except Exception as e:
        logger.error(f"Error getting AD scan status: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@active_directory_bp.route('/kerbrute/userenum/preview', methods=['POST'])
@jwt_required()
def preview_kerbrute_userenum():
    """Preview del comando Kerbrute userenum (sin ejecutar)."""
    data = request.get_json()
    domain = data.get('domain')
    dc_ip = data.get('dc_ip')
    userlist = data.get('userlist')
    workspace_id = data.get('workspace_id')
    
    if not all([domain, dc_ip, userlist, workspace_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        result = ad_service.preview_kerbrute_userenum(
            domain=domain,
            dc_ip=dc_ip,
            userlist=userlist,
            workspace_id=workspace_id
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_kerbrute_userenum: {e}")
        return jsonify({'error': str(e)}), 500


@active_directory_bp.route('/kerbrute/passwordspray/preview', methods=['POST'])
@jwt_required()
def preview_kerbrute_passwordspray():
    """Preview del comando Kerbrute passwordspray (sin ejecutar)."""
    data = request.get_json()
    domain = data.get('domain')
    dc_ip = data.get('dc_ip')
    userlist = data.get('userlist')
    password = data.get('password')
    workspace_id = data.get('workspace_id')
    
    if not all([domain, dc_ip, userlist, password, workspace_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        result = ad_service.preview_kerbrute_passwordspray(
            domain=domain,
            dc_ip=dc_ip,
            userlist=userlist,
            password=password,
            workspace_id=workspace_id
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_kerbrute_passwordspray: {e}")
        return jsonify({'error': str(e)}), 500


@active_directory_bp.route('/asreproast/preview', methods=['POST'])
@jwt_required()
def preview_getnpusers():
    """Preview del comando GetNPUsers (sin ejecutar)."""
    data = request.get_json()
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    
    if not all([domain, workspace_id]):
        return jsonify({'error': 'domain and workspace_id are required'}), 400
    
    try:
        result = ad_service.preview_getnpusers(
            domain=domain,
            workspace_id=workspace_id,
            username=data.get('username'),
            password=data.get('password'),
            dc_ip=data.get('dc_ip'),
            usersfile=data.get('usersfile'),
            no_pass=data.get('no_pass', True)
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_getnpusers: {e}")
        return jsonify({'error': str(e)}), 500


@active_directory_bp.route('/ldap/dump/preview', methods=['POST'])
@jwt_required()
def preview_ldapdomaindump():
    """Preview del comando ldapdomaindump (sin ejecutar)."""
    data = request.get_json()
    dc_ip = data.get('dc_ip')
    username = data.get('username')
    password = data.get('password')
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    
    if not all([dc_ip, username, password, domain, workspace_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        result = ad_service.preview_ldapdomaindump(
            dc_ip=dc_ip,
            username=username,
            password=password,
            domain=domain,
            workspace_id=workspace_id
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_ldapdomaindump: {e}")
        return jsonify({'error': str(e)}), 500


@active_directory_bp.route('/dns/dump/preview', methods=['POST'])
@jwt_required()
def preview_adidnsdump():
    """Preview del comando adidnsdump (sin ejecutar)."""
    data = request.get_json()
    dc_ip = data.get('dc_ip')
    username = data.get('username')
    password = data.get('password')
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    
    if not all([dc_ip, username, password, domain, workspace_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        result = ad_service.preview_adidnsdump(
            dc_ip=dc_ip,
            username=username,
            password=password,
            domain=domain,
            workspace_id=workspace_id
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_adidnsdump: {e}")
        return jsonify({'error': str(e)}), 500


@active_directory_bp.route('/cme/enum/users/preview', methods=['POST'])
@jwt_required()
def preview_cme_enum_users():
    """Preview del comando CrackMapExec enum users (sin ejecutar)."""
    data = request.get_json()
    dc_ip = data.get('dc_ip')
    username = data.get('username')
    password = data.get('password')
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    
    if not all([dc_ip, username, password, domain, workspace_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        result = ad_service.preview_cme_enum_users(
            dc_ip=dc_ip,
            username=username,
            password=password,
            domain=domain,
            workspace_id=workspace_id
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_cme_enum_users: {e}")
        return jsonify({'error': str(e)}), 500


@active_directory_bp.route('/cme/enum/groups', methods=['POST'])
@jwt_required()
def cme_enum_groups():
    """
    Enumera grupos con CrackMapExec.
    
    Body:
        {
            "dc_ip": "192.168.1.10",
            "username": "user",
            "password": "pass",
            "domain": "domain.com",
            "workspace_id": 1
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    dc_ip = data.get('dc_ip')
    username = data.get('username')
    password = data.get('password')
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    
    if not all([dc_ip, username, password, domain, workspace_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        result = ad_service.start_cme_enum_groups(
            dc_ip=dc_ip,
            username=username,
            password=password,
            domain=domain,
            workspace_id=workspace_id,
            user_id=int(current_user_id)
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in cme_enum_groups: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@active_directory_bp.route('/cme/enum/groups/preview', methods=['POST'])
@jwt_required()
def preview_cme_enum_groups():
    """Preview del comando CrackMapExec enum groups (sin ejecutar)."""
    data = request.get_json()
    dc_ip = data.get('dc_ip')
    username = data.get('username')
    password = data.get('password')
    domain = data.get('domain')
    workspace_id = data.get('workspace_id')
    
    if not all([dc_ip, username, password, domain, workspace_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        result = ad_service.preview_cme_enum_groups(
            dc_ip=dc_ip,
            username=username,
            password=password,
            domain=domain,
            workspace_id=workspace_id
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_cme_enum_groups: {e}")
        return jsonify({'error': str(e)}), 500


@active_directory_bp.route('/scans', methods=['GET'])
@jwt_required()
def list_ad_scans():
    """
    Lista todos los scans AD del workspace.
    """
    workspace_id = request.args.get('workspace_id', type=int)
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    from repositories import ScanRepository
    scan_repo = ScanRepository()
    
    try:
        scans = scan_repo.find_by_workspace(
            workspace_id=workspace_id,
            scan_type='active_directory'
        )
        
        return jsonify({
            'scans': [
                {
                    'scan_id': scan.id,
                    'status': scan.status,
                    'target': scan.target,
                    'tool': scan.options.get('tool'),
                    'action': scan.options.get('action'),
                    'started_at': scan.started_at.isoformat() if scan.started_at else None,
                    'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
                }
                for scan in scans
            ],
            'total': len(scans)
        }), 200
    except Exception as e:
        logger.error(f"Error listing AD scans: {e}")
        return jsonify({'error': 'Internal server error'}), 500
