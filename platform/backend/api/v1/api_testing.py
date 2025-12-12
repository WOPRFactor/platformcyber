"""
API Testing Endpoints
=====================

Endpoints para pentesting de APIs REST, GraphQL, SOAP.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import APITestingService

logger = logging.getLogger(__name__)

api_testing_bp = Blueprint('api_testing', __name__)

# Inicializar servicio
api_testing_service = APITestingService()


@api_testing_bp.route('/arjun', methods=['POST'])
@jwt_required()
def run_arjun():
    """
    Ejecuta Arjun para parameter discovery.
    
    Body:
        {
            "url": "https://api.example.com/endpoint",
            "workspace_id": 1,
            "methods": ["GET", "POST"],  // opcional
            "wordlist": "/path/to/wordlist.txt"  // opcional
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    url = data.get('url')
    workspace_id = data.get('workspace_id')
    
    if not all([url, workspace_id]):
        return jsonify({'error': 'url and workspace_id are required'}), 400
    
    try:
        result = api_testing_service.start_arjun_scan(
            url=url,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            methods=data.get('methods'),
            wordlist=data.get('wordlist')
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in run_arjun: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_testing_bp.route('/kiterunner', methods=['POST'])
@jwt_required()
def run_kiterunner():
    """
    Ejecuta Kiterunner para API route discovery.
    
    Body:
        {
            "url": "https://api.example.com",
            "workspace_id": 1,
            "wordlist": "/path/to/routes.txt",  // opcional
            "max_depth": 3  // opcional
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    url = data.get('url')
    workspace_id = data.get('workspace_id')
    
    if not all([url, workspace_id]):
        return jsonify({'error': 'url and workspace_id are required'}), 400
    
    try:
        result = api_testing_service.start_kiterunner_scan(
            url=url,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            wordlist=data.get('wordlist'),
            max_depth=data.get('max_depth', 3)
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in run_kiterunner: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_testing_bp.route('/jwt/analyze', methods=['POST'])
@jwt_required()
def analyze_jwt():
    """
    Analiza un JWT token.
    
    Body:
        {
            "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "workspace_id": 1,
            "crack_secret": false  // opcional
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    jwt_token = data.get('jwt_token')
    workspace_id = data.get('workspace_id')
    
    if not all([jwt_token, workspace_id]):
        return jsonify({'error': 'jwt_token and workspace_id are required'}), 400
    
    try:
        result = api_testing_service.analyze_jwt(
            jwt_token=jwt_token,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            crack_secret=data.get('crack_secret', False)
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in analyze_jwt: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_testing_bp.route('/ffuf', methods=['POST'])
@jwt_required()
def run_ffuf():
    """
    Ejecuta FFUF para fuzzing.
    
    Body:
        {
            "url": "https://example.com/FUZZ",
            "workspace_id": 1,
            "wordlist": "/usr/share/wordlists/dirb/common.txt",
            "fuzz_param": "FUZZ",  // opcional, default: FUZZ
            "filters": {  // opcional
                "status_codes": [200, 301, 302],
                "size": 1234,
                "words": 56
            }
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    url = data.get('url')
    workspace_id = data.get('workspace_id')
    wordlist = data.get('wordlist')
    
    if not all([url, workspace_id, wordlist]):
        return jsonify({'error': 'url, workspace_id, and wordlist are required'}), 400
    
    if 'FUZZ' not in url:
        return jsonify({'error': 'url must contain FUZZ placeholder'}), 400
    
    try:
        result = api_testing_service.start_ffuf_scan(
            url=url,
            workspace_id=workspace_id,
            user_id=int(current_user_id),
            wordlist=wordlist,
            fuzz_param=data.get('fuzz_param', 'FUZZ'),
            filters=data.get('filters')
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in run_ffuf: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_testing_bp.route('/graphql/introspect', methods=['POST'])
@jwt_required()
def graphql_introspect():
    """
    Ejecuta introspection de GraphQL.
    
    Body:
        {
            "url": "https://api.example.com/graphql",
            "workspace_id": 1
        }
    """
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    url = data.get('url')
    workspace_id = data.get('workspace_id')
    
    if not all([url, workspace_id]):
        return jsonify({'error': 'url and workspace_id are required'}), 400
    
    try:
        result = api_testing_service.graphql_introspect(
            url=url,
            workspace_id=workspace_id,
            user_id=int(current_user_id)
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in graphql_introspect: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_testing_bp.route('/scan/<int:scan_id>/results', methods=['GET'])
@jwt_required()
def get_api_scan_results(scan_id: int):
    """
    Obtiene resultados de un API testing scan.
    """
    try:
        results = api_testing_service.get_scan_results(scan_id)
        return jsonify(results), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting API scan results: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_testing_bp.route('/scan/<int:scan_id>', methods=['GET'])
@jwt_required()
def get_api_scan_status(scan_id: int):
    """
    Obtiene estado de un API testing scan.
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
        logger.error(f"Error getting API scan status: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_testing_bp.route('/scans', methods=['GET'])
@jwt_required()
def list_api_scans():
    """
    Lista todos los API testing scans del workspace.
    """
    workspace_id = request.args.get('workspace_id', type=int)
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    from repositories import ScanRepository
    scan_repo = ScanRepository()
    
    try:
        scans = scan_repo.find_by_workspace(
            workspace_id=workspace_id,
            scan_type='api_testing'
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
        logger.error(f"Error listing API scans: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_testing_bp.route('/tools', methods=['GET'])
@jwt_required()
def list_api_tools():
    """
    Lista las herramientas de API testing disponibles.
    """
    tools = [
        {
            'id': 'arjun',
            'name': 'Arjun',
            'description': 'HTTP parameter discovery tool',
            'category': 'Parameter Discovery',
            'methods': ['GET', 'POST', 'JSON']
        },
        {
            'id': 'kiterunner',
            'name': 'Kiterunner',
            'description': 'Fast API route discovery',
            'category': 'Route Discovery',
            'features': ['REST API', 'Custom wordlists', 'Deep scanning']
        },
        {
            'id': 'jwt_tool',
            'name': 'JWT_Tool',
            'description': 'JWT analysis and manipulation',
            'category': 'JWT Testing',
            'features': ['Decode', 'Verify', 'Crack secret', 'Forge tokens']
        },
        {
            'id': 'ffuf',
            'name': 'FFUF',
            'description': 'Fast web fuzzer',
            'category': 'Fuzzing',
            'features': ['Directories', 'Files', 'Parameters', 'Vhosts']
        },
        {
            'id': 'wfuzz',
            'name': 'Wfuzz',
            'description': 'Web application fuzzer',
            'category': 'Fuzzing',
            'features': ['Parameters', 'Directories', 'Files', 'Headers']
        },
        {
            'id': 'graphql',
            'name': 'GraphQL Introspection',
            'description': 'GraphQL schema discovery',
            'category': 'GraphQL',
            'features': ['Schema introspection', 'Query discovery', 'Mutation discovery']
        },
        {
            'id': 'postman',
            'name': 'Postman/Newman',
            'description': 'API testing automation',
            'category': 'Automation',
            'features': ['Collections', 'Environments', 'Test scripts']
        }
    ]
    
    return jsonify({
        'tools': tools,
        'total': len(tools),
        'categories': list(set(t['category'] for t in tools))
    }), 200
