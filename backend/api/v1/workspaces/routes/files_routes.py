"""
Files Routes for Workspaces
===========================

Rutas para gestión de archivos de workspaces.
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.files_service import WorkspaceFilesService
from pathlib import Path
from utils.workspace_filesystem import get_workspace_dir

files_service = WorkspaceFilesService()


def register_routes(bp: Blueprint):
    """Registra las rutas de archivos en el blueprint."""
    
    @bp.route('/<int:workspace_id>/files', methods=['GET', 'OPTIONS'])
    @jwt_required()
    def list_workspace_files(workspace_id):
        """Lista archivos generados en un workspace."""
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        try:
            user_id = int(get_jwt_identity())
            from repositories.workspace_repository import WorkspaceRepository
            workspace_repo = WorkspaceRepository()
            workspace = workspace_repo.find_by_id(workspace_id)
            
            if not workspace:
                return jsonify({'error': 'Not Found', 'message': 'Workspace not found'}), 404
            
            if workspace.owner_id != user_id:
                return jsonify({'error': 'Forbidden', 'message': 'Permission denied'}), 403
            
            category = request.args.get('category')
            relative_path = request.args.get('path', '')
            
            result = files_service.list_files(workspace_id, category=category, relative_path=relative_path)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': 'Bad Request', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Failed to list files', 'message': str(e)}), 500
    
    @bp.route('/<int:workspace_id>/files/<path:file_path>', methods=['GET', 'OPTIONS'])
    @jwt_required()
    def get_workspace_file(workspace_id, file_path):
        """Obtiene el contenido de un archivo del workspace."""
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        try:
            user_id = int(get_jwt_identity())
            from repositories.workspace_repository import WorkspaceRepository
            workspace_repo = WorkspaceRepository()
            workspace = workspace_repo.find_by_id(workspace_id)
            
            if not workspace:
                return jsonify({'error': 'Not Found', 'message': 'Workspace not found'}), 404
            
            if workspace.owner_id != user_id:
                return jsonify({'error': 'Forbidden', 'message': 'Permission denied'}), 403
            
            download = request.args.get('download', 'false').lower() == 'true'
            
            if download:
                workspace_dir = get_workspace_dir(workspace_id, workspace.name)
                full_path = workspace_dir / file_path
                try:
                    full_path.resolve().relative_to(workspace_dir.resolve())
                except ValueError:
                    return jsonify({'error': 'Bad Request', 'message': 'Invalid file path'}), 400
                
                if not full_path.exists() or not full_path.is_file():
                    return jsonify({'error': 'Not Found', 'message': 'File not found'}), 404
                
                return send_file(str(full_path), as_attachment=True, download_name=full_path.name)
            else:
                result = files_service.get_file(workspace_id, file_path)
                if result is None:
                    return jsonify({'error': 'Not Found', 'message': 'File not found'}), 404
                return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': 'Bad Request', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Failed to read file', 'message': str(e)}), 500
    
    @bp.route('/<int:workspace_id>/files/<path:file_path>', methods=['DELETE', 'OPTIONS'])
    @jwt_required()
    def delete_workspace_file(workspace_id, file_path):
        """Elimina un archivo específico del workspace."""
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        try:
            user_id = int(get_jwt_identity())
            from repositories.workspace_repository import WorkspaceRepository
            workspace_repo = WorkspaceRepository()
            workspace = workspace_repo.find_by_id(workspace_id)
            
            if not workspace:
                return jsonify({'error': 'Not Found', 'message': 'Workspace not found'}), 404
            
            if workspace.owner_id != user_id:
                return jsonify({'error': 'Forbidden', 'message': 'Permission denied'}), 403
            
            deleted = files_service.delete_file(workspace_id, file_path)
            if not deleted:
                return jsonify({'error': 'Not Found', 'message': 'File not found'}), 404
            
            return jsonify({'message': 'File deleted successfully', 'file_path': file_path}), 200
        except ValueError as e:
            return jsonify({'error': 'Bad Request', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Failed to delete file', 'message': str(e)}), 500
    
    @bp.route('/<int:workspace_id>/files', methods=['DELETE', 'OPTIONS'])
    @jwt_required()
    def delete_all_workspace_files(workspace_id):
        """Elimina todos los archivos del workspace."""
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        try:
            user_id = int(get_jwt_identity())
            from repositories.workspace_repository import WorkspaceRepository
            workspace_repo = WorkspaceRepository()
            workspace = workspace_repo.find_by_id(workspace_id)
            
            if not workspace:
                return jsonify({'error': 'Not Found', 'message': 'Workspace not found'}), 404
            
            if workspace.owner_id != user_id:
                return jsonify({'error': 'Forbidden', 'message': 'Permission denied'}), 403
            
            category = request.args.get('category')
            result = files_service.delete_all_files(workspace_id, category=category)
            
            if result is None:
                return jsonify({'error': 'Not Found', 'message': 'Workspace not found'}), 404
            
            return jsonify({
                'message': 'Files deleted successfully',
                'deleted_files': result['deleted_files'],
                'deleted_directories': result['deleted_directories'],
                'category': result['category']
            }), 200
        except ValueError as e:
            return jsonify({'error': 'Bad Request', 'message': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Failed to delete files', 'message': str(e)}), 500


