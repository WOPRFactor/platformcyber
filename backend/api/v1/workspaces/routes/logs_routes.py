"""
Logs Routes for Workspaces
=========================

Rutas para gestión de logs de workspaces.
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from ..services.logs_service import WorkspaceLogsService
import os

logs_service = WorkspaceLogsService()


def register_routes(bp: Blueprint):
    """Registra las rutas de logs en el blueprint."""
    
    @bp.route('/<int:workspace_id>/logs', methods=['GET'])
    @jwt_required()
    def get_workspace_logs(workspace_id):
        """Obtiene logs del workspace."""
        try:
            # Soporte para ambos formatos: limit/offset y page/per_page
            if 'page' in request.args and 'per_page' in request.args:
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 100, type=int)
                limit = per_page
                offset = (page - 1) * per_page
            else:
                limit = request.args.get('limit', 100, type=int)
                offset = request.args.get('offset', 0, type=int)
            
            level = request.args.get('level')
            source = request.args.get('source')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            result = logs_service.get_logs(
                workspace_id=workspace_id,
                limit=limit,
                offset=offset,
                level=level,
                source=source,
                start_date=start_date,
                end_date=end_date
            )
            
            if result is None:
                return jsonify({
                    'error': 'Not Found',
                    'message': 'Workspace not found'
                }), 404
            
            return jsonify(result), 200
        except Exception as e:
            return jsonify({
                'error': 'Failed to get workspace logs',
                'message': str(e)
            }), 500
    
    @bp.route('/<int:workspace_id>/logs/stats', methods=['GET'])
    @jwt_required()
    def get_workspace_logs_stats(workspace_id):
        """Obtiene estadísticas de logs del workspace."""
        try:
            stats = logs_service.get_logs_stats(workspace_id)
            
            if stats is None:
                return jsonify({
                    'error': 'Not Found',
                    'message': 'Workspace not found'
                }), 404
            
            return jsonify(stats), 200
        except Exception as e:
            return jsonify({
                'error': 'Failed to get logs stats',
                'message': str(e)
            }), 500
    
    @bp.route('/<int:workspace_id>/logs/export', methods=['GET'])
    @jwt_required()
    def export_workspace_logs(workspace_id):
        """Exporta logs del workspace."""
        try:
            file_path = logs_service.export_logs(workspace_id)
            
            if file_path is None:
                return jsonify({
                    'error': 'Not Found',
                    'message': 'Workspace not found'
                }), 404
            
            return send_file(
                file_path,
                mimetype='application/json',
                as_attachment=True,
                download_name=f'workspace_{workspace_id}_logs.json'
            )
        except Exception as e:
            return jsonify({
                'error': 'Failed to export logs',
                'message': str(e)
            }), 500
    
    @bp.route('/<int:workspace_id>/logs', methods=['DELETE'])
    @jwt_required()
    def delete_workspace_logs(workspace_id):
        """Elimina logs del workspace."""
        try:
            days = request.args.get('days', type=int)
            deleted = logs_service.delete_logs(workspace_id, days=days)
            
            if not deleted:
                return jsonify({
                    'error': 'Not Found',
                    'message': 'Workspace not found or no logs to delete'
                }), 404
            
            return jsonify({
                'message': 'Logs deleted successfully'
            }), 200
        except Exception as e:
            return jsonify({
                'error': 'Failed to delete logs',
                'message': str(e)
            }), 500

