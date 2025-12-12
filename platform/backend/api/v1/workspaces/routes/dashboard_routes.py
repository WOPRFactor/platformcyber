"""
Dashboard Routes for Workspaces
================================

Rutas para dashboard de workspaces.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.dashboard_service import WorkspaceDashboardService

dashboard_service = WorkspaceDashboardService()


def register_routes(bp: Blueprint):
    """Registra las rutas de dashboard en el blueprint."""
    
    @bp.route('/<int:workspace_id>/dashboard/stats', methods=['GET', 'OPTIONS'])
    @jwt_required()
    def get_dashboard_stats(workspace_id):
        """Obtiene métricas generales del dashboard."""
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        try:
            user_id = int(get_jwt_identity())
            from repositories.workspace_repository import WorkspaceRepository
            workspace_repo = WorkspaceRepository()
            workspace = workspace_repo.find_by_id(workspace_id)
            
            if not workspace:
                return jsonify({'error': 'Workspace not found'}), 404
            
            if workspace.owner_id != user_id:
                return jsonify({'error': 'Forbidden'}), 403
            
            stats = dashboard_service.get_stats(workspace_id)
            return jsonify(stats), 200
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    
    @bp.route('/<int:workspace_id>/dashboard/vulnerabilities', methods=['GET', 'OPTIONS'])
    @jwt_required()
    def get_dashboard_vulnerabilities(workspace_id):
        """Obtiene distribución de vulnerabilidades por severidad."""
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        try:
            user_id = int(get_jwt_identity())
            from repositories.workspace_repository import WorkspaceRepository
            workspace_repo = WorkspaceRepository()
            workspace = workspace_repo.find_by_id(workspace_id)
            
            if not workspace:
                return jsonify({'error': 'Workspace not found'}), 404
            
            if workspace.owner_id != user_id:
                return jsonify({'error': 'Forbidden'}), 403
            
            distribution = dashboard_service.get_vulnerabilities(workspace_id)
            return jsonify(distribution), 200
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    
    @bp.route('/<int:workspace_id>/dashboard/timeline', methods=['GET', 'OPTIONS'])
    @jwt_required()
    def get_dashboard_timeline(workspace_id):
        """Obtiene timeline de actividades."""
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        try:
            user_id = int(get_jwt_identity())
            from repositories.workspace_repository import WorkspaceRepository
            workspace_repo = WorkspaceRepository()
            workspace = workspace_repo.find_by_id(workspace_id)
            
            if not workspace:
                return jsonify({'error': 'Workspace not found'}), 404
            
            if workspace.owner_id != user_id:
                return jsonify({'error': 'Forbidden'}), 403
            
            days = request.args.get('days', 30, type=int)
            timeline = dashboard_service.get_timeline(workspace_id, days=days)
            return jsonify(timeline), 200
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    
    @bp.route('/<int:workspace_id>/dashboard/trends', methods=['GET', 'OPTIONS'])
    @jwt_required()
    def get_dashboard_trends(workspace_id):
        """Obtiene tendencias de vulnerabilidades."""
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        try:
            user_id = int(get_jwt_identity())
            from repositories.workspace_repository import WorkspaceRepository
            workspace_repo = WorkspaceRepository()
            workspace = workspace_repo.find_by_id(workspace_id)
            
            if not workspace:
                return jsonify({'error': 'Workspace not found'}), 404
            
            if workspace.owner_id != user_id:
                return jsonify({'error': 'Forbidden'}), 403
            
            days = request.args.get('days', 30, type=int)
            trends = dashboard_service.get_trends(workspace_id, days=days)
            return jsonify(trends), 200
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    
    @bp.route('/<int:workspace_id>/dashboard/top-vulnerabilities', methods=['GET', 'OPTIONS'])
    @jwt_required()
    def get_dashboard_top_vulnerabilities(workspace_id):
        """Obtiene top vulnerabilidades."""
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        try:
            user_id = int(get_jwt_identity())
            from repositories.workspace_repository import WorkspaceRepository
            workspace_repo = WorkspaceRepository()
            workspace = workspace_repo.find_by_id(workspace_id)
            
            if not workspace:
                return jsonify({'error': 'Workspace not found'}), 404
            
            if workspace.owner_id != user_id:
                return jsonify({'error': 'Forbidden'}), 403
            
            limit = request.args.get('limit', 10, type=int)
            top_vulns = dashboard_service.get_top_vulnerabilities(workspace_id, limit=limit)
            return jsonify(top_vulns), 200
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    
    @bp.route('/<int:workspace_id>/dashboard/risk-matrix', methods=['GET', 'OPTIONS'])
    @jwt_required()
    def get_dashboard_risk_matrix(workspace_id):
        """Obtiene datos para la matriz de riesgo."""
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        try:
            user_id = int(get_jwt_identity())
            from repositories.workspace_repository import WorkspaceRepository
            workspace_repo = WorkspaceRepository()
            workspace = workspace_repo.find_by_id(workspace_id)
            
            if not workspace:
                return jsonify({'error': 'Workspace not found'}), 404
            
            if workspace.owner_id != user_id:
                return jsonify({'error': 'Forbidden'}), 403
            
            risk_matrix = dashboard_service.get_risk_matrix(workspace_id)
            return jsonify(risk_matrix), 200
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

