"""
Preview Routes
==============

Rutas para preview de comandos de enumeración.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import logging

from services import ScanningService

logger = logging.getLogger(__name__)

scanning_service = ScanningService()


def register_routes(bp: Blueprint):
    """Registra las rutas de preview en el blueprint."""
    
    @bp.route('/enum/smb/enum4linux/preview', methods=['POST'])
    @jwt_required()
    def preview_enum4linux():
        """Preview del comando enum4linux."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            result = scanning_service.preview_enum4linux(
                target=target,
                workspace_id=workspace_id,
                use_ng=data.get('use_ng', True),
                all=data.get('all', False)
            )
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Error in preview_enum4linux: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/enum/smb/smbmap/preview', methods=['POST'])
    @jwt_required()
    def preview_smbmap():
        """Preview del comando smbmap."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            result = scanning_service.preview_smbmap(
                target=target,
                workspace_id=workspace_id,
                username=data.get('username'),
                password=data.get('password'),
                hash=data.get('hash'),
                recursive=data.get('recursive', False),
                share=data.get('share')
            )
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Error in preview_smbmap: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/enum/smb/smbclient/preview', methods=['POST'])
    @jwt_required()
    def preview_smbclient():
        """Preview del comando smbclient."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        share = data.get('share', 'IPC$')
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            result = scanning_service.preview_smbclient(
                target=target,
                workspace_id=workspace_id,
                share=share,
                username=data.get('username'),
                password=data.get('password'),
                command=data.get('command')
            )
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Error in preview_smbclient: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/enum/ftp/preview', methods=['POST'])
    @jwt_required()
    def preview_ftp_enum():
        """Preview del comando FTP enum."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        port = data.get('port', 21)
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.preview_ftp_enum(
                target=target,
                workspace_id=workspace_id,
                port=port
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_ftp_enum: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/enum/dns/preview', methods=['POST'])
    @jwt_required()
    def preview_dns_enum():
        """Preview del comando DNS enum."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        domain = data.get('domain')
        tool = data.get('tool', 'nmap')
        port = data.get('port', 53)
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.preview_dns_enum(
                target=target,
                workspace_id=workspace_id,
                domain=domain,
                tool=tool,
                port=port
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_dns_enum: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/enum/rdp/preview', methods=['POST'])
    @jwt_required()
    def preview_rdp_enum():
        """Preview del comando RDP enum."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        port = data.get('port', 3389)
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.preview_rdp_enum(
                target=target,
                workspace_id=workspace_id,
                port=port
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_rdp_enum: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/enum/ssh/preview', methods=['POST'])
    @jwt_required()
    def preview_ssh_enum():
        """Preview del comando SSH enum."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        tool = data.get('tool', 'nmap')
        port = data.get('port', 22)
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.preview_ssh_enum(
                target=target,
                workspace_id=workspace_id,
                tool=tool,
                port=port
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_ssh_enum: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/enum/smtp/preview', methods=['POST'])
    @jwt_required()
    def preview_smtp_enum():
        """Preview del comando SMTP enum."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        tool = data.get('tool', 'nmap')
        port = data.get('port', 25)
        userlist = data.get('userlist')
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.preview_smtp_enum(
                target=target,
                workspace_id=workspace_id,
                tool=tool,
                port=port,
                userlist=userlist
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_smtp_enum: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/enum/snmp/preview', methods=['POST'])
    @jwt_required()
    def preview_snmp_enum():
        """Preview del comando SNMP enum."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        tool = data.get('tool', 'nmap')
        port = data.get('port', 161)
        community = data.get('community', 'public')
        community_file = data.get('community_file')
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.preview_snmp_enum(
                target=target,
                workspace_id=workspace_id,
                tool=tool,
                port=port,
                community=community,
                community_file=community_file
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_snmp_enum: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/enum/ldap/preview', methods=['POST'])
    @jwt_required()
    def preview_ldap_enum():
        """Preview del comando LDAP enum."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        tool = data.get('tool', 'nmap')
        port = data.get('port', 389)
        base_dn = data.get('base_dn')
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.preview_ldap_enum(
                target=target,
                workspace_id=workspace_id,
                tool=tool,
                port=port,
                base_dn=base_dn
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_ldap_enum: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/enum/mysql/preview', methods=['POST'])
    @jwt_required()
    def preview_mysql_enum():
        """Preview del comando MySQL enum."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        tool = data.get('tool', 'nmap')
        port = data.get('port', 3306)
        username = data.get('username')
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.preview_mysql_enum(
                target=target,
                workspace_id=workspace_id,
                tool=tool,
                port=port,
                username=username
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_mysql_enum: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/enum/postgresql/preview', methods=['POST'])
    @jwt_required()
    def preview_postgresql_enum():
        """Preview del comando PostgreSQL enum."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        tool = data.get('tool', 'nmap')
        port = data.get('port', 5432)
        username = data.get('username', 'postgres')
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.preview_postgresql_enum(
                target=target,
                workspace_id=workspace_id,
                tool=tool,
                port=port,
                username=username
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_postgresql_enum: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/enum/redis/preview', methods=['POST'])
    @jwt_required()
    def preview_redis_enum():
        """Preview del comando Redis enum."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        tool = data.get('tool', 'nmap')
        port = data.get('port', 6379)
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.preview_redis_enum(
                target=target,
                workspace_id=workspace_id,
                tool=tool,
                port=port
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_redis_enum: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/enum/mongodb/preview', methods=['POST'])
    @jwt_required()
    def preview_mongodb_enum():
        """Preview del comando MongoDB enum."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        port = data.get('port', 27017)
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.preview_mongodb_enum(
                target=target,
                workspace_id=workspace_id,
                port=port
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_mongodb_enum: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/enum/ssl/sslscan/preview', methods=['POST'])
    @jwt_required()
    def preview_sslscan():
        """Preview del comando sslscan."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        port = data.get('port', 443)
        show_certificate = data.get('show_certificate', False)
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.preview_sslscan(
                target=target,
                workspace_id=workspace_id,
                port=port,
                show_certificate=show_certificate
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_sslscan: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @bp.route('/enum/ssl/sslyze/preview', methods=['POST'])
    @jwt_required()
    def preview_sslyze():
        """Preview del comando sslyze."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        port = data.get('port', 443)
        regular = data.get('regular', True)
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            if isinstance(port, str):
                port = int(port)
            result = scanning_service.preview_sslyze(
                target=target,
                workspace_id=workspace_id,
                port=port,
                regular=regular
            )
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error in preview_sslyze: {e}")
            return jsonify({'error': 'Internal server error'}), 500


