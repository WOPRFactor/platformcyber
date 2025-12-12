"""
Evidence Routes for Workspaces
===============================

Rutas para gestión de evidencias de workspaces.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from repositories.workspace_repository import WorkspaceRepository

workspace_repo = WorkspaceRepository()


def register_routes(bp: Blueprint):
    """Registra las rutas de evidencias en el blueprint."""
    
    @bp.route('/<int:workspace_id>/evidence', methods=['GET', 'OPTIONS'])
    def get_workspace_evidence(workspace_id):
        """Obtiene evidencias de un workspace."""
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
            return jsonify({'error': 'Failed to get evidence', 'message': str(e)}), 500
    
    @bp.route('/<int:workspace_id>/evidence', methods=['POST', 'OPTIONS'])
    def create_workspace_evidence(workspace_id):
        """Crea nueva evidencia en un workspace."""
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
            
            return jsonify({'error': 'Not Implemented', 'message': 'Evidence creation not yet implemented'}), 501
        except Exception as e:
            return jsonify({'error': 'Failed to create evidence', 'message': str(e)}), 500
    
    @bp.route('/<int:workspace_id>/evidence/<int:evidence_id>', methods=['PUT', 'OPTIONS'])
    def update_workspace_evidence(workspace_id, evidence_id):
        """Actualiza evidencia existente."""
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
            
            return jsonify({'error': 'Not Implemented', 'message': 'Evidence update not yet implemented'}), 501
        except Exception as e:
            return jsonify({'error': 'Failed to update evidence', 'message': str(e)}), 500
    
    @bp.route('/<int:workspace_id>/evidence/<int:evidence_id>', methods=['DELETE', 'OPTIONS'])
    def delete_workspace_evidence(workspace_id, evidence_id):
        """Elimina evidencia."""
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
            
            return jsonify({'error': 'Not Implemented', 'message': 'Evidence deletion not yet implemented'}), 501
        except Exception as e:
            return jsonify({'error': 'Failed to delete evidence', 'message': str(e)}), 500


