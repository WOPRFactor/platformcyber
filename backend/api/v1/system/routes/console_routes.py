"""
Console Routes
==============

Rutas para ejecución de comandos de consola.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
import logging
import subprocess
import os

logger = logging.getLogger(__name__)


def register_routes(bp: Blueprint):
    """Registra las rutas de consola."""
    
    @bp.route('/console/execute', methods=['POST'])
    @jwt_required()
    def execute_console_command():
        """
        Ejecuta un comando de forma segura en el servidor.
        
        Body:
            {
                "command": "nmap -sV -p 80 example.com"
            }
        
        Returns:
            {
                "success": true,
                "output": "...",
                "returncode": 0,
                "error": null
            }
        """
        try:
            data = request.get_json()
            command_str = data.get('command', '').strip()
            
            if not command_str:
                return jsonify({'error': 'Command is required'}), 400
            
            from utils.validators.command_sanitizer import CommandSanitizer
            import shlex
            
            try:
                parts = shlex.split(command_str)
                if not parts:
                    return jsonify({'error': 'Invalid command'}), 400
                
                command_base = parts[0]
                args = parts[1:] if len(parts) > 1 else []
                
                safe_command = CommandSanitizer.sanitize_command(command_base, args, allow_unsafe=False)
                
            except ValueError as e:
                logger.warning(f"Command sanitization failed: {e}")
                return jsonify({'error': f'Command not allowed: {str(e)}'}), 400
            except Exception as e:
                logger.error(f"Error parsing command: {e}")
                return jsonify({'error': 'Invalid command format'}), 400
            
            try:
                result = subprocess.run(
                    safe_command,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    env=CommandSanitizer.get_safe_env(),
                    cwd=os.getcwd()
                )
                
                return jsonify({
                    'success': True,
                    'output': result.stdout,
                    'error': result.stderr if result.stderr else None,
                    'returncode': result.returncode,
                    'command': ' '.join(safe_command)
                }), 200
                
            except subprocess.TimeoutExpired:
                return jsonify({
                    'success': False,
                    'error': 'Command timeout (5 minutes)',
                    'returncode': -1
                }), 408
            except Exception as e:
                logger.error(f"Error executing command: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'returncode': -1
                }), 500
                
        except Exception as e:
            logger.error(f"Error in execute_console_command: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


