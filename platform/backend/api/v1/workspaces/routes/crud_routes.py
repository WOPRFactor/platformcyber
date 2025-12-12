"""
CRUD Routes for Workspaces
==========================

Rutas básicas CRUD para workspaces.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.workspace_service import WorkspaceService

workspace_service = WorkspaceService()


def register_routes(bp: Blueprint):
    """Registra las rutas CRUD en el blueprint."""
    
    @bp.route('/', methods=['GET'])
    @jwt_required()
    def list_workspaces():
        """Lista todos los workspaces del usuario actual."""
        try:
            user_id = int(get_jwt_identity())
            workspaces = workspace_service.list_workspaces(user_id)
            return jsonify(workspaces), 200
        except Exception as e:
            return jsonify({
                'error': 'Failed to list workspaces',
                'message': str(e)
            }), 500
    
    @bp.route('/<int:workspace_id>', methods=['GET'])
    @jwt_required()
    def get_workspace(workspace_id):
        """Obtiene un workspace específico."""
        try:
            workspace = workspace_service.get_workspace(workspace_id)
            if not workspace:
                return jsonify({
                    'error': 'Not Found',
                    'message': 'Workspace not found'
                }), 404
            return jsonify(workspace), 200
        except Exception as e:
            return jsonify({
                'error': 'Failed to get workspace',
                'message': str(e)
            }), 500
    
    @bp.route('/', methods=['POST'])
    @jwt_required()
    def create_workspace():
        """Crea un nuevo workspace."""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data.get('name'):
                return jsonify({
                    'error': 'Validation Error',
                    'message': 'Workspace name is required'
                }), 400
            
            workspace = workspace_service.create_workspace(user_id, data)
            return jsonify(workspace), 201
        except Exception as e:
            return jsonify({
                'error': 'Failed to create workspace',
                'message': str(e)
            }), 500
    
    @bp.route('/<int:workspace_id>', methods=['PUT'])
    @jwt_required()
    def update_workspace(workspace_id):
        """Actualiza un workspace existente."""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            workspace = workspace_service.update_workspace(workspace_id, user_id, data)
            if not workspace:
                return jsonify({
                    'error': 'Not Found',
                    'message': 'Workspace not found'
                }), 404
            
            return jsonify(workspace), 200
        except PermissionError as e:
            return jsonify({
                'error': 'Forbidden',
                'message': str(e)
            }), 403
        except Exception as e:
            return jsonify({
                'error': 'Failed to update workspace',
                'message': str(e)
            }), 500
    
    @bp.route('/<int:workspace_id>', methods=['DELETE'])
    @jwt_required()
    def delete_workspace(workspace_id):
        """Elimina un workspace."""
        try:
            user_id = int(get_jwt_identity())
            deleted = workspace_service.delete_workspace(workspace_id, user_id)
            
            if not deleted:
                return jsonify({
                    'error': 'Not Found',
                    'message': 'Workspace not found'
                }), 404
            
            return jsonify({
                'message': 'Workspace deleted successfully'
            }), 200
        except PermissionError as e:
            return jsonify({
                'error': 'Forbidden',
                'message': str(e)
            }), 403
        except Exception as e:
            return jsonify({
                'error': 'Failed to delete workspace',
                'message': str(e)
            }), 500
    
    @bp.route('/<int:workspace_id>/archive', methods=['POST'])
    @jwt_required()
    def archive_workspace(workspace_id):
        """Archiva un workspace."""
        try:
            user_id = int(get_jwt_identity())
            workspace = workspace_service.archive_workspace(workspace_id, user_id)
            
            if not workspace:
                return jsonify({
                    'error': 'Not Found',
                    'message': 'Workspace not found'
                }), 404
            
            return jsonify({
                'message': 'Workspace archived successfully',
                'workspace': workspace
            }), 200
        except PermissionError as e:
            return jsonify({
                'error': 'Forbidden',
                'message': str(e)
            }), 403
        except Exception as e:
            return jsonify({
                'error': 'Failed to archive workspace',
                'message': str(e)
            }), 500


