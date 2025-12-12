"""
Health Routes
=============

Rutas para health checks e información del sistema.
"""

from flask import Blueprint, jsonify
from datetime import datetime, timezone

def register_routes(bp: Blueprint):
    """Registra las rutas de health."""
    
    @bp.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'version': '3.0.0',
            'environment': 'development',
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }), 200
    
    @bp.route('/info', methods=['GET'])
    def system_info():
        """Información del sistema."""
        return jsonify({
            'name': 'Pentesting Platform',
            'version': '3.0.0',
            'api_version': 'v1',
            'environment': 'development',
            'features': [
                'reconnaissance',
                'scanning',
                'vulnerability_assessment',
                'exploitation',
                'post_exploitation',
                'active_directory',
                'cloud_pentesting',
                'api_testing',
                'reporting'
            ]
        }), 200


