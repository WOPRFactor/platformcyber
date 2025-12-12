"""
Database Enumeration Routes
===========================

Rutas para enumeración de bases de datos.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from services import ScanningService

logger = logging.getLogger(__name__)

scanning_service = ScanningService()


def register_routes(bp: Blueprint):
    """Registra las rutas de enumeración de bases de datos en el blueprint."""
    
    @bp.route('/enum/mysql', methods=['POST'])
    @jwt_required()
    def mysql_enum():
        """Enumeración MySQL."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        current_user_id = get_jwt_identity()
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            result = scanning_service.start_mysql_enum(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                port=data.get('port', 3306),
                tool=data.get('tool', 'nmap'),
                username=data.get('username')
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error in MySQL enum: {e}")
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/enum/postgresql', methods=['POST'])
    @jwt_required()
    def postgresql_enum():
        """Enumeración PostgreSQL."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        current_user_id = get_jwt_identity()
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            result = scanning_service.start_postgresql_enum(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                port=data.get('port', 5432),
                tool=data.get('tool', 'nmap'),
                username=data.get('username', 'postgres')
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error in PostgreSQL enum: {e}")
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/enum/redis', methods=['POST'])
    @jwt_required()
    def redis_enum():
        """Enumeración Redis."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        current_user_id = get_jwt_identity()
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            result = scanning_service.start_redis_enum(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                port=data.get('port', 6379),
                tool=data.get('tool', 'nmap')
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error in Redis enum: {e}")
            return jsonify({'error': str(e)}), 500
    
    @bp.route('/enum/mongodb', methods=['POST'])
    @jwt_required()
    def mongodb_enum():
        """Enumeración MongoDB."""
        data = request.get_json()
        target = data.get('target')
        workspace_id = data.get('workspace_id')
        current_user_id = get_jwt_identity()
        
        if not target or not workspace_id:
            return jsonify({'error': 'target and workspace_id required'}), 400
        
        try:
            result = scanning_service.start_mongodb_enum(
                target=target,
                workspace_id=workspace_id,
                user_id=current_user_id,
                port=data.get('port', 27017)
            )
            return jsonify(result), 201
        except Exception as e:
            logger.error(f"Error in MongoDB enum: {e}")
            return jsonify({'error': str(e)}), 500


