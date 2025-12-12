"""
Mobile Security Endpoints
==========================

Endpoints para pentesting de aplicaciones móviles (Android/iOS).
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services.mobile_service import MobileService

logger = logging.getLogger(__name__)

mobile_bp = Blueprint('mobile', __name__)

# Inicializar servicio
mobile_service = MobileService()


@mobile_bp.route('/mobsf/analyze', methods=['POST'])
@jwt_required()
def run_mobsf_analysis():
    """
    Ejecuta análisis con MobSF.
    
    Body:
        {
            "apk_path": "/path/to/app.apk",
            "workspace_id": 1,
            "analysis_type": "static"  // "static" o "dynamic"
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    apk_path = data.get('apk_path')
    workspace_id = data.get('workspace_id')
    
    if not all([apk_path, workspace_id]):
        return jsonify({'error': 'apk_path and workspace_id are required'}), 400
    
    try:
        result = mobile_service.start_mobsf_analysis(
            apk_path=apk_path,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            analysis_type=data.get('analysis_type', 'static')
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in run_mobsf_analysis: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@mobile_bp.route('/apktool/decompile', methods=['POST'])
@jwt_required()
def decompile_apk():
    """
    Decompila un APK con APKTool.
    
    Body:
        {
            "apk_path": "/path/to/app.apk",
            "workspace_id": 1,
            "decode_resources": true  // opcional
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    apk_path = data.get('apk_path')
    workspace_id = data.get('workspace_id')
    
    if not all([apk_path, workspace_id]):
        return jsonify({'error': 'apk_path and workspace_id are required'}), 400
    
    try:
        result = mobile_service.decompile_apk(
            apk_path=apk_path,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            decode_resources=data.get('decode_resources', True)
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in decompile_apk: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@mobile_bp.route('/frida/trace', methods=['POST'])
@jwt_required()
def start_frida_trace():
    """
    Inicia tracing con Frida.
    
    Body:
        {
            "package_name": "com.example.app",
            "workspace_id": 1,
            "trace_functions": ["Java.*", "android.app.*"],  // opcional
            "device_id": "emulator-5554"  // opcional
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    package_name = data.get('package_name')
    workspace_id = data.get('workspace_id')
    
    if not all([package_name, workspace_id]):
        return jsonify({'error': 'package_name and workspace_id are required'}), 400
    
    try:
        result = mobile_service.start_frida_trace(
            package_name=package_name,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            trace_functions=data.get('trace_functions'),
            device_id=data.get('device_id')
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in start_frida_trace: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@mobile_bp.route('/objection/explore', methods=['POST'])
@jwt_required()
def run_objection_explore():
    """
    Ejecuta comandos de Objection.
    
    Body:
        {
            "package_name": "com.example.app",
            "workspace_id": 1,
            "commands": [  // opcional
                "env",
                "android hooking list classes",
                "android intent launch_activity"
            ]
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    package_name = data.get('package_name')
    workspace_id = data.get('workspace_id')
    
    if not all([package_name, workspace_id]):
        return jsonify({'error': 'package_name and workspace_id are required'}), 400
    
    try:
        result = mobile_service.start_objection_explore(
            package_name=package_name,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            commands=data.get('commands')
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in run_objection_explore: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@mobile_bp.route('/scan/<int:scan_id>/results', methods=['GET'])
@jwt_required()
def get_mobile_scan_results(scan_id: int):
    """
    Obtiene resultados de un mobile security scan.
    """
    try:
        results = mobile_service.get_scan_results(scan_id)
        return jsonify(results), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting mobile scan results: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@mobile_bp.route('/scan/<int:scan_id>', methods=['GET'])
@jwt_required()
def get_mobile_scan_status(scan_id: int):
    """
    Obtiene estado de un mobile security scan.
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
        logger.error(f"Error getting mobile scan status: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@mobile_bp.route('/scans', methods=['GET'])
@jwt_required()
def list_mobile_scans():
    """
    Lista todos los mobile security scans del workspace.
    """
    workspace_id = request.args.get('workspace_id', type=int)
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    from repositories import ScanRepository
    scan_repo = ScanRepository()
    
    try:
        scans = scan_repo.find_by_workspace(
            workspace_id=workspace_id,
            scan_type='mobile_security'
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
        logger.error(f"Error listing mobile scans: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@mobile_bp.route('/tools', methods=['GET'])
@jwt_required()
def list_mobile_tools():
    """
    Lista las herramientas de mobile security disponibles.
    """
    tools = [
        {
            'id': 'mobsf',
            'name': 'MobSF',
            'description': 'Mobile Security Framework - All-in-one mobile app security platform',
            'category': 'Static & Dynamic Analysis',
            'platforms': ['Android', 'iOS'],
            'features': [
                'Static analysis',
                'Dynamic analysis',
                'Malware analysis',
                'API fuzzing'
            ]
        },
        {
            'id': 'apktool',
            'name': 'APKTool',
            'description': 'Tool for reverse engineering Android APK files',
            'category': 'Decompilation',
            'platforms': ['Android'],
            'features': [
                'Decode resources',
                'Rebuild APK',
                'Access to AndroidManifest.xml',
                'Smali code extraction'
            ]
        },
        {
            'id': 'frida',
            'name': 'Frida',
            'description': 'Dynamic instrumentation toolkit',
            'category': 'Runtime Analysis',
            'platforms': ['Android', 'iOS', 'Windows', 'macOS', 'Linux'],
            'features': [
                'Function tracing',
                'Method hooking',
                'Memory manipulation',
                'SSL pinning bypass'
            ]
        },
        {
            'id': 'objection',
            'name': 'Objection',
            'description': 'Runtime mobile exploration powered by Frida',
            'category': 'Runtime Analysis',
            'platforms': ['Android', 'iOS'],
            'features': [
                'Runtime class exploration',
                'SSL pinning bypass',
                'Root/Jailbreak detection bypass',
                'File system access'
            ]
        }
    ]
    
    return jsonify({
        'tools': tools,
        'total': len(tools),
        'categories': list(set(t['category'] for t in tools)),
        'platforms': list(set(p for t in tools for p in t.get('platforms', [])))
    }), 200



