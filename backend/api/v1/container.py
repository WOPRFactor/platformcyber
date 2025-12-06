"""
Container Security Endpoints
=============================

Endpoints para pentesting de contenedores y Kubernetes.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services.container import ContainerService

logger = logging.getLogger(__name__)

container_bp = Blueprint('container', __name__)

# Inicializar servicio
container_service = ContainerService()


@container_bp.route('/trivy/image', methods=['POST'])
@jwt_required()
def scan_image_trivy():
    """
    Escanea imagen Docker con Trivy.
    
    Body:
        {
            "image": "nginx:latest",
            "workspace_id": 1,
            "severity": ["CRITICAL", "HIGH"]  // opcional
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    image = data.get('image')
    workspace_id = data.get('workspace_id')
    
    if not all([image, workspace_id]):
        return jsonify({'error': 'image and workspace_id are required'}), 400
    
    try:
        result = container_service.scan_image_trivy(
            image=image,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            severity=data.get('severity')
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in scan_image_trivy: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@container_bp.route('/grype/image', methods=['POST'])
@jwt_required()
def scan_image_grype():
    """
    Escanea imagen con Grype.
    
    Body:
        {
            "image": "ubuntu:22.04",
            "workspace_id": 1,
            "scope": "all-layers"  // opcional: "all-layers" o "squashed"
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    image = data.get('image')
    workspace_id = data.get('workspace_id')
    
    if not all([image, workspace_id]):
        return jsonify({'error': 'image and workspace_id are required'}), 400
    
    try:
        result = container_service.scan_image_grype(
            image=image,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            scope=data.get('scope', 'all-layers')
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in scan_image_grype: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@container_bp.route('/syft/sbom', methods=['POST'])
@jwt_required()
def generate_sbom():
    """
    Genera SBOM con Syft.
    
    Body:
        {
            "image": "alpine:3.18",
            "workspace_id": 1,
            "output_format": "spdx-json"  // opcional: spdx-json, cyclonedx-json, syft-json
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    image = data.get('image')
    workspace_id = data.get('workspace_id')
    
    if not all([image, workspace_id]):
        return jsonify({'error': 'image and workspace_id are required'}), 400
    
    try:
        result = container_service.generate_sbom(
            image=image,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            output_format=data.get('output_format', 'spdx-json')
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in generate_sbom: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@container_bp.route('/kube-hunter/scan', methods=['POST'])
@jwt_required()
def run_kubehunter():
    """
    Ejecuta Kube-hunter para pentest de Kubernetes.
    
    Body:
        {
            "workspace_id": 1,
            "mode": "remote",  // "remote", "internal", "network"
            "remote_host": "k8s.example.com"  // requerido si mode=remote
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    workspace_id = data.get('workspace_id')
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    mode = data.get('mode', 'remote')
    
    if mode == 'remote' and not data.get('remote_host'):
        return jsonify({'error': 'remote_host is required for mode=remote'}), 400
    
    try:
        result = container_service.run_kubehunter(
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            mode=mode,
            remote_host=data.get('remote_host')
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in run_kubehunter: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@container_bp.route('/kube-bench/run', methods=['POST'])
@jwt_required()
def run_kubebench():
    """
    Ejecuta Kube-bench (CIS Kubernetes Benchmark).
    
    Body:
        {
            "workspace_id": 1,
            "targets": ["master", "node", "etcd"]  // opcional
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    workspace_id = data.get('workspace_id')
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    try:
        result = container_service.run_kubebench(
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            targets=data.get('targets')
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in run_kubebench: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@container_bp.route('/kubescape/scan', methods=['POST'])
@jwt_required()
def run_kubescape():
    """
    Ejecuta Kubescape para security scanning de K8s.
    
    Body:
        {
            "workspace_id": 1,
            "framework": "nsa",  // "nsa", "mitre", "armobest"
            "namespace": "default"  // opcional
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    workspace_id = data.get('workspace_id')
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    try:
        result = container_service.run_kubescape(
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            framework=data.get('framework', 'nsa'),
            namespace=data.get('namespace')
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in run_kubescape: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@container_bp.route('/scan/<int:scan_id>/results', methods=['GET'])
@jwt_required()
def get_container_scan_results(scan_id: int):
    """
    Obtiene resultados de un container security scan.
    """
    try:
        results = container_service.get_scan_results(scan_id)
        return jsonify(results), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting container scan results: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@container_bp.route('/scan/<int:scan_id>', methods=['GET'])
@jwt_required()
def get_container_scan_status(scan_id: int):
    """
    Obtiene estado de un container security scan.
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
            'started_at': scan.started_at.isoformat() if scan.started_at else None,
            'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
        }), 200
    except Exception as e:
        logger.error(f"Error getting container scan status: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@container_bp.route('/scans', methods=['GET'])
@jwt_required()
def list_container_scans():
    """
    Lista todos los container security scans del workspace.
    """
    workspace_id = request.args.get('workspace_id', type=int)
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    from repositories import ScanRepository
    scan_repo = ScanRepository()
    
    try:
        scans = scan_repo.find_by_workspace(
            workspace_id=workspace_id,
            scan_type='container_security'
        )
        
        return jsonify({
            'scans': [
                {
                    'scan_id': scan.id,
                    'status': scan.status,
                    'target': scan.target,
                    'tool': scan.options.get('tool'),
                    'started_at': scan.started_at.isoformat() if scan.started_at else None,
                    'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
                }
                for scan in scans
            ],
            'total': len(scans)
        }), 200
    except Exception as e:
        logger.error(f"Error listing container scans: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@container_bp.route('/trivy/image/preview', methods=['POST'])
@jwt_required()
def preview_trivy_scan():
    """Preview del comando Trivy (sin ejecutar)."""
    data = request.get_json()
    image = data.get('image')
    workspace_id = data.get('workspace_id')
    
    if not all([image, workspace_id]):
        return jsonify({'error': 'image and workspace_id are required'}), 400
    
    try:
        result = container_service.preview_trivy_scan(
            image=image,
            workspace_id=workspace_id,
            severity=data.get('severity')
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_trivy_scan: {e}")
        return jsonify({'error': str(e)}), 500


@container_bp.route('/grype/image/preview', methods=['POST'])
@jwt_required()
def preview_grype_scan():
    """Preview del comando Grype (sin ejecutar)."""
    data = request.get_json()
    image = data.get('image')
    workspace_id = data.get('workspace_id')
    
    if not all([image, workspace_id]):
        return jsonify({'error': 'image and workspace_id are required'}), 400
    
    try:
        result = container_service.preview_grype_scan(
            image=image,
            workspace_id=workspace_id,
            scope=data.get('scope', 'all-layers')
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_grype_scan: {e}")
        return jsonify({'error': str(e)}), 500


@container_bp.route('/syft/sbom/preview', methods=['POST'])
@jwt_required()
def preview_syft_sbom():
    """Preview del comando Syft (sin ejecutar)."""
    data = request.get_json()
    image = data.get('image')
    workspace_id = data.get('workspace_id')
    
    if not all([image, workspace_id]):
        return jsonify({'error': 'image and workspace_id are required'}), 400
    
    try:
        result = container_service.preview_syft_sbom(
            image=image,
            workspace_id=workspace_id,
            output_format=data.get('output_format', 'spdx-json')
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_syft_sbom: {e}")
        return jsonify({'error': str(e)}), 500


@container_bp.route('/kube-hunter/scan/preview', methods=['POST'])
@jwt_required()
def preview_kubehunter():
    """Preview del comando Kube-hunter (sin ejecutar)."""
    data = request.get_json()
    workspace_id = data.get('workspace_id')
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    try:
        result = container_service.preview_kubehunter(
            workspace_id=workspace_id,
            mode=data.get('mode', 'remote'),
            remote_host=data.get('remote_host')
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_kubehunter: {e}")
        return jsonify({'error': str(e)}), 500


@container_bp.route('/kube-bench/run/preview', methods=['POST'])
@jwt_required()
def preview_kubebench():
    """Preview del comando Kube-bench (sin ejecutar)."""
    data = request.get_json()
    workspace_id = data.get('workspace_id')
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    try:
        result = container_service.preview_kubebench(
            workspace_id=workspace_id,
            targets=data.get('targets')
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_kubebench: {e}")
        return jsonify({'error': str(e)}), 500


@container_bp.route('/kubescape/scan/preview', methods=['POST'])
@jwt_required()
def preview_kubescape():
    """Preview del comando Kubescape (sin ejecutar)."""
    data = request.get_json()
    workspace_id = data.get('workspace_id')
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    try:
        result = container_service.preview_kubescape(
            workspace_id=workspace_id,
            framework=data.get('framework', 'nsa'),
            namespace=data.get('namespace')
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error in preview_kubescape: {e}")
        return jsonify({'error': str(e)}), 500


@container_bp.route('/tools', methods=['GET'])
@jwt_required()
def list_container_tools():
    """
    Lista las herramientas de container security disponibles.
    """
    tools = [
        {
            'id': 'trivy',
            'name': 'Trivy',
            'description': 'Comprehensive security scanner for containers',
            'category': 'Image Scanning',
            'features': [
                'CVE detection',
                'OS packages scanning',
                'Application dependencies',
                'IaC scanning'
            ]
        },
        {
            'id': 'grype',
            'name': 'Grype',
            'description': 'Vulnerability scanner for container images and filesystems',
            'category': 'Image Scanning',
            'features': [
                'Multi-source vulnerability matching',
                'SBOM scanning',
                'Fast scanning',
                'Detailed reports'
            ]
        },
        {
            'id': 'syft',
            'name': 'Syft',
            'description': 'SBOM (Software Bill of Materials) generator',
            'category': 'SBOM',
            'features': [
                'SPDX format',
                'CycloneDX format',
                'Package discovery',
                'Container & filesystem support'
            ]
        },
        {
            'id': 'kube-hunter',
            'name': 'Kube-hunter',
            'description': 'Kubernetes penetration testing tool',
            'category': 'K8s Security',
            'features': [
                'Active hunting',
                'Passive detection',
                'Remote scanning',
                'Network mapping'
            ]
        },
        {
            'id': 'kube-bench',
            'name': 'Kube-bench',
            'description': 'CIS Kubernetes Benchmark checker',
            'category': 'K8s Compliance',
            'features': [
                'CIS benchmarks',
                'Master node checks',
                'Worker node checks',
                'etcd checks'
            ]
        },
        {
            'id': 'kubescape',
            'name': 'Kubescape',
            'description': 'Kubernetes security platform',
            'category': 'K8s Security',
            'features': [
                'NSA/CISA framework',
                'MITRE ATT&CK',
                'Risk assessment',
                'Compliance checking'
            ]
        }
    ]
    
    return jsonify({
        'tools': tools,
        'total': len(tools),
        'categories': list(set(t['category'] for t in tools))
    }), 200



