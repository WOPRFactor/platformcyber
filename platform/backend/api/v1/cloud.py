"""
Cloud Pentesting API Endpoints
===============================

Endpoints para pentesting en entornos cloud (AWS, Azure, GCP).
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import CloudService

logger = logging.getLogger(__name__)

cloud_bp = Blueprint('cloud', __name__)

# Inicializar servicio
cloud_service = CloudService()


@cloud_bp.route('/pacu/module', methods=['POST'])
@jwt_required()
def run_pacu_module():
    """
    Ejecuta un módulo de Pacu (AWS).
    
    Body:
        {
            "module_name": "iam__enum_permissions",
            "workspace_id": 1,
            "aws_profile": "default",  // opcional
            "module_args": {           // opcional
                "arg1": "value1"
            }
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    module_name = data.get('module_name')
    workspace_id = data.get('workspace_id')
    
    if not all([module_name, workspace_id]):
        return jsonify({'error': 'module_name and workspace_id are required'}), 400
    
    try:
        result = cloud_service.start_pacu_module(
            module_name=module_name,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            aws_profile=data.get('aws_profile'),
            module_args=data.get('module_args')
        )
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error in run_pacu_module: {e}")
        return jsonify({'error': str(e)}), 500


@cloud_bp.route('/scoutsuite/scan', methods=['POST'])
@jwt_required()
def run_scoutsuite():
    """
    Ejecuta ScoutSuite para auditoría multi-cloud.
    
    Body:
        {
            "provider": "aws|azure|gcp|alibaba|oci",
            "workspace_id": 1,
            "profile": "default",       // opcional
            "regions": ["us-east-1"],   // opcional
            "services": ["iam", "s3"]   // opcional
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    provider = data.get('provider')
    workspace_id = data.get('workspace_id')
    
    if not all([provider, workspace_id]):
        return jsonify({'error': 'provider and workspace_id are required'}), 400
    
    valid_providers = ['aws', 'azure', 'gcp', 'alibaba', 'oci']
    if provider not in valid_providers:
        return jsonify({'error': f'Invalid provider. Must be one of: {valid_providers}'}), 400
    
    try:
        result = cloud_service.start_scoutsuite_scan(
            provider=provider,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            profile=data.get('profile'),
            regions=data.get('regions'),
            services=data.get('services')
        )
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error in run_scoutsuite: {e}")
        return jsonify({'error': str(e)}), 500


@cloud_bp.route('/prowler/scan', methods=['POST'])
@jwt_required()
def run_prowler():
    """
    Ejecuta Prowler para auditoría de seguridad cloud.
    
    Body:
        {
            "provider": "aws|azure|gcp",
            "workspace_id": 1,
            "profile": "default",                    // opcional
            "severity": ["critical", "high"],        // opcional
            "compliance": "cis",                     // opcional (cis, hipaa, gdpr, pci)
            "services": ["iam", "s3"]                // opcional
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    provider = data.get('provider')
    workspace_id = data.get('workspace_id')
    
    if not all([provider, workspace_id]):
        return jsonify({'error': 'provider and workspace_id are required'}), 400
    
    valid_providers = ['aws', 'azure', 'gcp']
    if provider not in valid_providers:
        return jsonify({'error': f'Invalid provider. Must be one of: {valid_providers}'}), 400
    
    try:
        result = cloud_service.start_prowler_scan(
            provider=provider,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            profile=data.get('profile'),
            severity=data.get('severity'),
            compliance=data.get('compliance'),
            services=data.get('services')
        )
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error in run_prowler: {e}")
        return jsonify({'error': str(e)}), 500


@cloud_bp.route('/azurehound/collect', methods=['POST'])
@jwt_required()
def run_azurehound():
    """
    Ejecuta AzureHound para enumerar Azure AD.
    
    Body:
        {
            "tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            "workspace_id": 1,
            "username": "user@domain.com",  // opcional si access_token
            "password": "password",         // opcional si access_token
            "access_token": "eyJ0..."       // opcional si username/password
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    tenant_id = data.get('tenant_id')
    workspace_id = data.get('workspace_id')
    
    if not all([tenant_id, workspace_id]):
        return jsonify({'error': 'tenant_id and workspace_id are required'}), 400
    
    try:
        result = cloud_service.start_azurehound_collection(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            username=data.get('username'),
            password=data.get('password'),
            access_token=data.get('access_token')
        )
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error in run_azurehound: {e}")
        return jsonify({'error': str(e)}), 500


@cloud_bp.route('/roadtools/gather', methods=['POST'])
@jwt_required()
def run_roadtools():
    """
    Ejecuta ROADtools para recopilar datos de Azure AD.
    
    Body:
        {
            "workspace_id": 1,
            "username": "user@domain.com",  // opcional si access_token
            "password": "password",         // opcional si access_token
            "access_token": "eyJ0...",      // opcional si username/password
            "tenant_id": "xxx..."           // opcional
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    workspace_id = data.get('workspace_id')
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    try:
        result = cloud_service.start_roadrecon_gather(
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            username=data.get('username'),
            password=data.get('password'),
            access_token=data.get('access_token'),
            tenant_id=data.get('tenant_id')
        )
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error in run_roadtools: {e}")
        return jsonify({'error': str(e)}), 500


@cloud_bp.route('/scan/<int:scan_id>/results', methods=['GET'])
@jwt_required()
def get_cloud_scan_results(scan_id: int):
    """
    Obtiene resultados de un cloud scan.
    """
    try:
        results = cloud_service.get_scan_results(scan_id)
        return jsonify(results), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting cloud scan results: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@cloud_bp.route('/scan/<int:scan_id>', methods=['GET'])
@jwt_required()
def get_cloud_scan_status(scan_id: int):
    """
    Obtiene estado de un cloud scan.
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
            'provider': scan.options.get('provider'),
            'started_at': scan.started_at.isoformat() if scan.started_at else None,
            'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
        }), 200
    except Exception as e:
        logger.error(f"Error getting cloud scan status: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@cloud_bp.route('/scans', methods=['GET'])
@jwt_required()
def list_cloud_scans():
    """
    Lista todos los cloud scans del workspace.
    """
    workspace_id = request.args.get('workspace_id', type=int)
    provider = request.args.get('provider')  # Filtro opcional
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    from repositories import ScanRepository
    scan_repo = ScanRepository()
    
    try:
        scans = scan_repo.find_by_workspace(
            workspace_id=workspace_id,
            scan_type='cloud_pentesting'
        )
        
        # Filtrar por provider si se especifica
        if provider:
            scans = [s for s in scans if s.options.get('provider') == provider]
        
        return jsonify({
            'scans': [
                {
                    'scan_id': scan.id,
                    'status': scan.status,
                    'target': scan.target,
                    'tool': scan.options.get('tool'),
                    'provider': scan.options.get('provider'),
                    'started_at': scan.started_at.isoformat() if scan.started_at else None,
                    'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
                }
                for scan in scans
            ],
            'total': len(scans)
        }), 200
    except Exception as e:
        logger.error(f"Error listing cloud scans: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@cloud_bp.route('/providers', methods=['GET'])
@jwt_required()
def list_providers():
    """
    Lista los proveedores cloud soportados.
    """
    return jsonify({
        'providers': {
            'aws': {
                'name': 'Amazon Web Services',
                'tools': ['pacu', 'scoutsuite', 'prowler']
            },
            'azure': {
                'name': 'Microsoft Azure',
                'tools': ['scoutsuite', 'prowler', 'azurehound', 'roadtools']
            },
            'gcp': {
                'name': 'Google Cloud Platform',
                'tools': ['scoutsuite', 'prowler']
            },
            'alibaba': {
                'name': 'Alibaba Cloud',
                'tools': ['scoutsuite']
            },
            'oci': {
                'name': 'Oracle Cloud Infrastructure',
                'tools': ['scoutsuite']
            }
        }
    }), 200


@cloud_bp.route('/pacu/module/preview', methods=['POST'])
@jwt_required()
def preview_pacu_module():
    """
    Preview del comando Pacu (sin ejecutar).
    
    Body:
        {
            "module_name": "iam__enum_permissions",
            "workspace_id": 1,
            "aws_profile": "default",  // opcional
            "module_args": {           // opcional
                "arg1": "value1"
            }
        }
    """
    data = request.get_json()
    workspace_id = data.get('workspace_id')
    module_name = data.get('module_name')
    
    if not all([module_name, workspace_id]):
        return jsonify({'error': 'module_name and workspace_id are required'}), 400
    
    try:
        result = cloud_service.preview_pacu_module(
            module_name=module_name,
            workspace_id=workspace_id,
            aws_profile=data.get('aws_profile'),
            module_args=data.get('module_args')
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_pacu_module: {e}")
        return jsonify({'error': str(e)}), 500


@cloud_bp.route('/scoutsuite/scan/preview', methods=['POST'])
@jwt_required()
def preview_scoutsuite_scan():
    """
    Preview del comando ScoutSuite (sin ejecutar).
    """
    data = request.get_json()
    provider = data.get('provider')
    workspace_id = data.get('workspace_id')
    
    if not all([provider, workspace_id]):
        return jsonify({'error': 'provider and workspace_id are required'}), 400
    
    try:
        result = cloud_service.preview_scoutsuite_scan(
            provider=provider,
            workspace_id=workspace_id,
            profile=data.get('profile'),
            regions=data.get('regions'),
            services=data.get('services')
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_scoutsuite_scan: {e}")
        return jsonify({'error': str(e)}), 500


@cloud_bp.route('/prowler/scan/preview', methods=['POST'])
@jwt_required()
def preview_prowler_scan():
    """
    Preview del comando Prowler (sin ejecutar).
    """
    data = request.get_json()
    provider = data.get('provider')
    workspace_id = data.get('workspace_id')
    
    if not all([provider, workspace_id]):
        return jsonify({'error': 'provider and workspace_id are required'}), 400
    
    try:
        result = cloud_service.preview_prowler_scan(
            provider=provider,
            workspace_id=workspace_id,
            profile=data.get('profile'),
            severity=data.get('severity'),
            compliance=data.get('compliance'),
            services=data.get('services')
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_prowler_scan: {e}")
        return jsonify({'error': str(e)}), 500


@cloud_bp.route('/azurehound/collect/preview', methods=['POST'])
@jwt_required()
def preview_azurehound_collection():
    """
    Preview del comando AzureHound (sin ejecutar).
    """
    data = request.get_json()
    tenant_id = data.get('tenant_id')
    workspace_id = data.get('workspace_id')
    
    if not all([tenant_id, workspace_id]):
        return jsonify({'error': 'tenant_id and workspace_id are required'}), 400
    
    try:
        result = cloud_service.preview_azurehound_collection(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            username=data.get('username'),
            password=data.get('password'),
            access_token=data.get('access_token')
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_azurehound_collection: {e}")
        return jsonify({'error': str(e)}), 500


@cloud_bp.route('/roadtools/gather/preview', methods=['POST'])
@jwt_required()
def preview_roadrecon_gather():
    """
    Preview del comando ROADtools (sin ejecutar).
    """
    data = request.get_json()
    workspace_id = data.get('workspace_id')
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    try:
        result = cloud_service.preview_roadrecon_gather(
            workspace_id=workspace_id,
            username=data.get('username'),
            password=data.get('password'),
            access_token=data.get('access_token'),
            tenant_id=data.get('tenant_id')
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_roadrecon_gather: {e}")
        return jsonify({'error': str(e)}), 500


@cloud_bp.route('/pacu/modules', methods=['GET'])
@jwt_required()
def list_pacu_modules():
    """
    Lista los módulos disponibles de Pacu (informativo).
    """
    # Módulos más comunes de Pacu
    modules = {
        'reconnaissance': [
            'iam__enum_permissions',
            'iam__enum_users_roles_policies',
            'iam__bruteforce_permissions',
            'ec2__enum',
            's3__bucket_finder'
        ],
        'enumeration': [
            'ec2__enum_instances',
            'lambda__enum',
            'rds__enum_snapshots',
            's3__enum',
            'cloudtrail__enum'
        ],
        'persistence': [
            'iam__backdoor_users_keys',
            'iam__backdoor_assume_role',
            'lambda__backdoor_new_roles'
        ],
        'privilege_escalation': [
            'iam__privesc_scan'
        ],
        'lateral_movement': [
            'ec2__startup_shell_script'
        ],
        'exfiltration': [
            's3__download_bucket',
            'rds__explore_snapshots',
            'ebs__explore_snapshots'
        ]
    }
    
    return jsonify({
        'tool': 'pacu',
        'categories': modules,
        'total_modules': sum(len(mods) for mods in modules.values())
    }), 200
