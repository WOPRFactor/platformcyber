"""
Sessions Routes for Workspaces
===============================

Rutas para gestión de sesiones de workspaces.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from repositories.workspace_repository import WorkspaceRepository

workspace_repo = WorkspaceRepository()


def register_routes(bp: Blueprint):
    """Registra las rutas de sesiones en el blueprint."""
    
    @bp.route('/<int:workspace_id>/sessions', methods=['GET', 'OPTIONS'])
    def get_workspace_sessions(workspace_id):
        """Obtiene sesiones de un workspace."""
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()
        except Exception:
            return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
        
        try:
            workspace = workspace_repo.find_by_id(workspace_id)
            if not workspace:
                return jsonify({'error': 'Not Found', 'message': 'Workspace not found'}), 404
            
            user_id = int(get_jwt_identity())
            if workspace.owner_id != user_id:
                return jsonify({'error': 'Forbidden', 'message': 'Permission denied'}), 403
            
            # Por ahora devolver array vacío hasta que se implementen los modelos
            return jsonify([]), 200
        except Exception as e:
            return jsonify({'error': 'Failed to get sessions', 'message': str(e)}), 500
    
    @bp.route('/<int:workspace_id>/sessions', methods=['POST', 'OPTIONS'])
    def create_workspace_session(workspace_id):
        """Crea una nueva sesión en un workspace."""
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()
        except Exception:
            return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
        
        try:
            workspace = workspace_repo.find_by_id(workspace_id)
            if not workspace:
                return jsonify({'error': 'Not Found', 'message': 'Workspace not found'}), 404
            
            user_id = int(get_jwt_identity())
            if workspace.owner_id != user_id:
                return jsonify({'error': 'Forbidden', 'message': 'Permission denied'}), 403
            
            return jsonify({'error': 'Not Implemented', 'message': 'Session creation not yet implemented'}), 501
        except Exception as e:
            return jsonify({'error': 'Failed to create session', 'message': str(e)}), 500


