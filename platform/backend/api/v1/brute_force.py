"""
Brute Force API Endpoints
==========================

Endpoints REST para ataques de fuerza bruta con Hydra.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.brute_force_service import BruteForceService
from repositories import ScanRepository
import logging

logger = logging.getLogger(__name__)

brute_force_bp = Blueprint('brute_force', __name__)
brute_force_service = BruteForceService()
scan_repo = ScanRepository()


@brute_force_bp.route('/hydra', methods=['POST'])
@jwt_required()
def hydra_attack():
    """
    Ejecuta ataque de fuerza bruta con Hydra.
    
    Body:
        {
            "target": "192.168.1.100",
            "service": "ssh",
            "username": "admin",  // O username_list
            "password_list": "/path/to/passwords.txt",
            "port": 22,
            "workspace_id": 1,
            "options": {
                "threads": 4,
                "timeout": 30,
                "verbose": false,
                "exit_on_first": true
            }
        }
    
    Returns:
        {
            "scan_id": 123,
            "status": "running",
            "message": "Hydra attack started"
        }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['target', 'service', 'workspace_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validar que se proporcione username o username_list
        if 'username' not in data and 'username_list' not in data:
            return jsonify({'error': 'Must provide username or username_list'}), 400
        
        # Validar que se proporcione password o password_list
        if 'password' not in data and 'password_list' not in data:
            return jsonify({'error': 'Must provide password or password_list'}), 400
        
        target = data['target']
        service = data['service']
        workspace_id = data['workspace_id']
        
        # Crear scan en DB
        scan = scan_repo.create(
            scan_type='brute_force',
            target=target,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'hydra',
                'service': service,
                **data.get('options', {})
            }
        )
        
        # Ejecutar Hydra (asíncrono con Celery en producción)
        try:
            from tasks.brute_force_tasks import hydra_attack_task
            
            # Ejecutar task asíncrona
            task = hydra_attack_task.delay(
                scan_id=scan.id,
                target=target,
                service=service,
                username=data.get('username'),
                username_list=data.get('username_list'),
                password=data.get('password'),
                password_list=data.get('password_list'),
                port=data.get('port'),
                options=data.get('options', {})
            )
            
            # Actualizar scan con task_id
            scan_repo.update_progress(scan, 0, 'Hydra attack queued')
            
            return jsonify({
                'scan_id': scan.id,
                'task_id': task.id,
                'status': 'queued',
                'message': f'Hydra attack against {target}:{service} queued'
            }), 201
            
        except ImportError:
            # Fallback: ejecución síncrona (solo para desarrollo)
            logger.warning("Celery not available, running Hydra synchronously")
            
            result = brute_force_service.hydra_attack(
                target=target,
                service=service,
                username=data.get('username'),
                username_list=data.get('username_list'),
                password=data.get('password'),
                password_list=data.get('password_list'),
                port=data.get('port'),
                options=data.get('options', {})
            )
            
            # Actualizar scan
            if result['status'] == 'completed':
                scan_repo.update_status(scan, 'completed')
                scan_repo.update_progress(scan, 100, 'Hydra attack completed')
            else:
                scan_repo.update_status(scan, 'failed')
                scan_repo.update_progress(scan, 0, f"Error: {result.get('error', 'Unknown')}")
            
            return jsonify({
                'scan_id': scan.id,
                'status': result['status'],
                'valid_credentials': result.get('valid_credentials', []),
                'attempts': result.get('attempts'),
                'output_file': result.get('output_file')
            }), 201
    
    except ValueError as e:
        logger.error(f"Validation error in Hydra attack: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error starting Hydra attack: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@brute_force_bp.route('/hydra/modules', methods=['GET'])
@jwt_required()
def get_hydra_modules():
    """
    Obtiene lista de módulos soportados por Hydra.
    
    Returns:
        {
            "modules": ["ssh", "ftp", "http-get", ...]
        }
    """
    try:
        modules = brute_force_service.get_hydra_modules()
        
        return jsonify({
            'modules': modules,
            'count': len(modules)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting Hydra modules: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@brute_force_bp.route('/wordlists/common-passwords', methods=['GET'])
@jwt_required()
def get_common_passwords():
    """
    Obtiene lista de contraseñas comunes.
    
    Query params:
        count: Número de contraseñas (default: 100)
    
    Returns:
        {
            "passwords": ["password", "123456", ...],
            "count": 100
        }
    """
    try:
        count = request.args.get('count', 100, type=int)
        
        if count < 1 or count > 1000:
            return jsonify({'error': 'Count must be between 1 and 1000'}), 400
        
        passwords = brute_force_service.get_common_passwords(count)
        
        return jsonify({
            'passwords': passwords,
            'count': len(passwords)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting common passwords: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@brute_force_bp.route('/wordlists/common-usernames', methods=['GET'])
@jwt_required()
def get_common_usernames():
    """
    Obtiene lista de usuarios comunes.
    
    Query params:
        count: Número de usuarios (default: 50)
    
    Returns:
        {
            "usernames": ["admin", "root", ...],
            "count": 50
        }
    """
    try:
        count = request.args.get('count', 50, type=int)
        
        if count < 1 or count > 500:
            return jsonify({'error': 'Count must be between 1 and 500'}), 400
        
        usernames = brute_force_service.get_common_usernames(count)
        
        return jsonify({
            'usernames': usernames,
            'count': len(usernames)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting common usernames: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@brute_force_bp.route('/wordlists/create', methods=['POST'])
@jwt_required()
def create_wordlist():
    """
    Crea un archivo wordlist personalizado.
    
    Body:
        {
            "filename": "my_wordlist.txt",
            "words": ["word1", "word2", ...]
        }
    
    Returns:
        {
            "path": "/path/to/wordlist.txt",
            "count": 100
        }
    """
    try:
        data = request.get_json()
        
        if 'filename' not in data or 'words' not in data:
            return jsonify({'error': 'Missing filename or words'}), 400
        
        filename = data['filename']
        words = data['words']
        
        if not isinstance(words, list):
            return jsonify({'error': 'Words must be a list'}), 400
        
        if len(words) < 1:
            return jsonify({'error': 'Words list cannot be empty'}), 400
        
        # Crear wordlist
        import os
        output_path = os.path.join(
            brute_force_service.output_dir,
            filename
        )
        
        path = brute_force_service.create_wordlist(output_path, words)
        
        return jsonify({
            'path': path,
            'count': len(words),
            'message': 'Wordlist created successfully'
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating wordlist: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@brute_force_bp.route('/check-installation', methods=['GET'])
@jwt_required()
def check_installation():
    """
    Verifica si Hydra está instalado.
    
    Returns:
        {
            "installed": true,
            "tool": "hydra"
        }
    """
    try:
        installed = brute_force_service.check_hydra_installed()
        
        return jsonify({
            'installed': installed,
            'tool': 'hydra',
            'message': 'Hydra is installed' if installed else 'Hydra is not installed'
        }), 200
    
    except Exception as e:
        logger.error(f"Error checking Hydra installation: {e}")
        return jsonify({'error': 'Internal server error'}), 500



