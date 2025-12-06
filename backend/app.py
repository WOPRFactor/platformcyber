#!/usr/bin/env python3
"""
Cybersecurity Pentesting Platform - Backend API
================================================

Plataforma de pentesting automatizado con integración IA.

Autor: Factor X
Fecha: Noviembre 2025
Versión: 3.0.0 (Refactorizada)
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import get_config
from models import db, init_db

# Importar blueprints de API v1
from api.v1 import (
    auth_bp,
    reconnaissance_bp,
    scanning_bp,
    vulnerability_bp,
    exploitation_bp,
    post_exploitation_bp,
    active_directory_bp,
    cloud_bp,
    api_testing_bp,
    mobile_bp,
    container_bp,
    reporting_bp,
    system_bp,
    owasp_bp,
    advanced_bp,
    mitre_bp
)
from api.v1.integrations import integrations_bp
from api.v1.workspaces import workspaces_bp
from api.v1.brute_force import brute_force_bp
from api.v1.impacket import impacket_bp
from api.v1.websocket_api import websocket_bp
from api.v1.pentest_selector import pentest_selector_bp

# Importar Socket.IO
from websockets import socketio

# Importar Prometheus metrics
from monitoring import setup_metrics

# Importar Performance optimizations
from utils.cache import init_cache
from utils.compression import setup_compression

logger = logging.getLogger(__name__)


def create_app(config_name: str = 'development') -> Flask:
    """
    Application Factory Pattern.
    
    Crea y configura la aplicación Flask.
    
    Args:
        config_name: Nombre de la configuración ('development', 'production', 'testing')
    
    Returns:
        Aplicación Flask configurada
        from flask_cors import CORS
    app = Flask(__name__)
    CORS(app)
    """
    app = Flask(__name__)
    
    # Cargar configuración
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Inicializar extensiones
    init_extensions(app)
    
    # Setup Prometheus metrics
    setup_metrics(app)
    
    # Setup response compression
    setup_compression(app, min_size=500)
    
    # Initialize Redis cache
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/2')
    init_cache(redis_url)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Configurar logging
    setup_logging(app)
    
    # Configurar handlers de errores
    register_error_handlers(app)
    
    # Inicializar base de datos
    with app.app_context():
        init_db(app)
    
    # Inicializar scheduler
    from services.scheduler_service import scheduler_service
    scheduler_service.start()
    
    logger.info(f"✅ Aplicación iniciada en modo {config_name}")
    
    return app


def init_extensions(app: Flask) -> None:
    """Inicializa extensiones Flask."""
    
    # Base de datos
    db.init_app(app)
    
    # Socket.IO
    socketio.init_app(app)
    
    # CORS
    # CORS - Configuración para desarrollo y producción
    import os
    is_production = os.getenv('FLASK_ENV') == 'production'
    
    if is_production:
        allowed_origins = [
            "https://tu-dominio-produccion.com"  # TODO: Cambiar en producción
        ]
    else:
        # En desarrollo: permitir cualquier origen de la LAN (192.168.x.x) y localhost
        # Esto permite acceso desde cualquier máquina en la red local
        allowed_origins = [
            "http://192.168.0.11:5178",
            "http://192.168.0.11:5179",
            "http://192.168.0.11:5379",
            "http://localhost:5173",
            "http://localhost:5178",
            "http://localhost:5179",
            "http://localhost:5379",
            # Permitir cualquier IP de la LAN con regex
            r"http://192\.168\.\d+\.\d+:\d+",
            r"http://localhost:\d+"
        ]
    
    CORS(app, 
         resources={r"/api/*": {
             "origins": allowed_origins,
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             "allow_headers": ["Content-Type", "Authorization", "X-Project-ID"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True
         }},
         automatic_options=True)  # Asegurar que OPTIONS se maneje automáticamente

    # Permitir OPTIONS sin autenticación (CORS preflight)
    # Flask-CORS maneja esto automáticamente con automatic_options=True
    # Este handler es solo para casos especiales si es necesario
    
    # Logging de todas las peticiones entrantes
    @app.before_request
    def log_request():
        """Registra todas las peticiones entrantes."""
        # Saltar logging para OPTIONS (ya se manejan arriba)
        if request.method == 'OPTIONS':
            return
        
        if request.path.startswith('/api/'):
            logger.info(f"🌐 REQUEST: {request.method} {request.path}")
            try:
                if request.is_json:
                    logger.info(f"   JSON Body: {request.get_json()}")
                elif request.form:
                    logger.info(f"   Form Data: {dict(request.form)}")
                elif request.args:
                    logger.info(f"   Query Params: {dict(request.args)}")
            except Exception as e:
                logger.error(f"   Error leyendo body: {e}")
    
    # Agregar after_request handler para asegurar headers CORS en TODAS las respuestas
    # Esto es necesario porque Flask-CORS a veces no procesa errores 500 correctamente
    @app.after_request
    def after_request_handler(response):
        """Asegura que todas las respuestas tengan headers CORS, incluso en errores."""
        # Solo agregar headers si no están ya presentes (para evitar duplicación)
        if 'Access-Control-Allow-Origin' not in response.headers:
            origin = request.headers.get('Origin')
            # Verificar si el origen está en la lista de orígenes permitidos
            # Usar la misma lista que se configuró en CORS
            if origin:
                # Para desarrollo, permitir los orígenes conocidos
                dev_origins = [
                    "http://192.168.0.11:5178",
                    "http://192.168.0.11:5179",
                    "http://192.168.0.11:5379",
                    "http://localhost:5173",
                    "http://localhost:5178",
                    "http://localhost:5179",
                    "http://localhost:5379"
                ]
                if origin in dev_origins:
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers['Access-Control-Allow-Credentials'] = 'true'
                    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
                    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Project-ID'
                    response.headers['Access-Control-Expose-Headers'] = 'Content-Type, Authorization'
        return response
    
    # JWT
    jwt = JWTManager(app)
    
    # Helper para agregar headers CORS (usado en handlers JWT)
    from flask import request as flask_request
    
    def add_cors_headers_jwt(response):
        """Agrega headers CORS a una respuesta."""
        origin = flask_request.headers.get('Origin')
        if origin:
            dev_origins = [
                "http://192.168.0.11:5178",
                "http://192.168.0.11:5179",
                "http://192.168.0.11:5379",
                "http://localhost:5173",
                "http://localhost:5178",
                "http://localhost:5179",
                "http://localhost:5379"
            ]
            if origin in dev_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Project-ID'
                response.headers['Access-Control-Expose-Headers'] = 'Content-Type, Authorization'
        return response
    
    # Handler para errores de JWT
    from flask import jsonify, request as flask_request
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        logger.error(f"❌ JWT Invalid Token: {error_string}")
        logger.error(f"   Path: {flask_request.path}")
        logger.error(f"   Method: {flask_request.method}")
        logger.error(f"   Headers: {dict(flask_request.headers)}")
        response = jsonify({'error': 'Invalid token', 'message': error_string})
        return add_cors_headers_jwt(response), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.error(f"❌ JWT Expired Token")
        logger.error(f"   Path: {flask_request.path}")
        logger.error(f"   Method: {flask_request.method}")
        response = jsonify({'error': 'Token expired', 'message': 'Token has expired'})
        return add_cors_headers_jwt(response), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        logger.error(f"❌ JWT Unauthorized: {error_string}")
        logger.error(f"   Path: {flask_request.path}")
        logger.error(f"   Method: {flask_request.method}")
        response = jsonify({'error': 'Unauthorized', 'message': error_string})
        return add_cors_headers_jwt(response), 401
    
    # Rate limiting
    # En desarrollo, aumentar límites para permitir polling frecuente
    import os
    is_production = os.getenv('FLASK_ENV') == 'production'
    rate_limits = app.config['RATE_LIMIT_DEFAULT'] if is_production else ["10000 per day", "1000 per hour"]
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=rate_limits,
        storage_uri=app.config.get('RATE_LIMIT_STORAGE_URI', 'memory://')
    )
    
    # Excluir peticiones OPTIONS del rate limiting (necesarias para CORS preflight)
    @limiter.request_filter
    def exempt_requests():
        # Excluir OPTIONS (CORS preflight)
        if request.method == 'OPTIONS':
            return True
        
        # Excluir endpoints de status de scans (polling frecuente necesario)
        path = request.path
        if request.method == 'GET' and '/scans/' in path:
            # Excluir GET /api/v1/reconnaissance/scans/<id> (status)
            # Excluir GET /api/v1/system/running-scans
            if path.endswith('/running-scans') or (
                '/reconnaissance/scans/' in path or 
                '/scanning/scans/' in path or
                '/vulnerability/scans/' in path
            ):
                # Verificar que no sea un endpoint de resultados o subdominios
                if '/results' not in path and '/subdomains' not in path:
                    return True
        
        return False
    
    logger.info("✅ Extensiones inicializadas")


def register_blueprints(app: Flask) -> None:
    """Registra todos los blueprints de la API."""
    
    # API v1
    api_prefix = '/api/v1'
    
    app.register_blueprint(auth_bp, url_prefix=f'{api_prefix}/auth')
    app.register_blueprint(reconnaissance_bp, url_prefix=f'{api_prefix}/reconnaissance')
    app.register_blueprint(scanning_bp, url_prefix=f'{api_prefix}/scanning')
    app.register_blueprint(vulnerability_bp, url_prefix=f'{api_prefix}/vulnerability')
    app.register_blueprint(exploitation_bp, url_prefix=f'{api_prefix}/exploitation')
    app.register_blueprint(post_exploitation_bp, url_prefix=f'{api_prefix}/post-exploitation')
    app.register_blueprint(active_directory_bp, url_prefix=f'{api_prefix}/active-directory')
    app.register_blueprint(cloud_bp, url_prefix=f'{api_prefix}/cloud')
    app.register_blueprint(api_testing_bp, url_prefix=f'{api_prefix}/api-testing')
    app.register_blueprint(mobile_bp, url_prefix=f'{api_prefix}/mobile')
    app.register_blueprint(container_bp, url_prefix=f'{api_prefix}/container')
    app.register_blueprint(brute_force_bp, url_prefix=f'{api_prefix}/brute-force')
    app.register_blueprint(impacket_bp, url_prefix=f'{api_prefix}/impacket')
    app.register_blueprint(reporting_bp, url_prefix=f'{api_prefix}/reporting')
    app.register_blueprint(workspaces_bp, url_prefix=f'{api_prefix}/workspaces')
    app.register_blueprint(owasp_bp, url_prefix=f'{api_prefix}/owasp')
    app.register_blueprint(websocket_bp, url_prefix=f'{api_prefix}/websocket')
    app.register_blueprint(pentest_selector_bp)  # Ya tiene url_prefix en la definición
    app.register_blueprint(advanced_bp, url_prefix=f'{api_prefix}/advanced')
    app.register_blueprint(mitre_bp, url_prefix=f'{api_prefix}/mitre')
    app.register_blueprint(integrations_bp, url_prefix=f'{api_prefix}/integrations')
    
    # Registrar system_bp AL FINAL para evitar conflictos
    app.register_blueprint(system_bp, url_prefix=f'{api_prefix}/system')
    
    logger.info("✅ Blueprints registrados")


def setup_logging(app: Flask) -> None:
    """
    Configura logging estructurado con rotación automática.
    
    Los logs se guardan en la ruta especificada por LOG_DIR (variable de entorno),
    que debe apuntar al directorio logs/ del entorno (dev/logs, test/logs, prod/logs).
    """
    
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_dir = os.getenv('LOG_DIR') or app.config.get('LOG_DIR', 'logs')
    log_file = app.config.get('LOG_FILE', 'app.log')
    log_max_bytes = app.config.get('LOG_MAX_BYTES', 50 * 1024 * 1024)  # 50MB
    log_backup_count = app.config.get('LOG_BACKUP_COUNT', 3)
    
    # Determinar ruta del log
    # Si LOG_DIR es absoluto, usarlo directamente
    # Si es relativo, resolverlo desde el directorio actual de trabajo
    if os.path.isabs(log_dir):
        log_path = Path(log_dir) / log_file
    else:
        # Resolver desde el directorio actual (donde se ejecuta la app)
        # En producción, esto debería ser el directorio del entorno
        cwd = Path.cwd()
        log_path = cwd / log_dir / log_file
    
    # Crear directorio si no existe
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configurar formato
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Handler para archivo con rotación
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=log_max_bytes,
        backupCount=log_backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, log_level))
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # Handler para consola (solo en desarrollo)
    if app.config.get('DEBUG', False):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        console_handler.setFormatter(log_format)
        root_logger.addHandler(console_handler)
    
    # Silenciar logs innecesarios
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    logger.info(f"✅ Logging configurado: {log_path}")
    logger.info(f"   Rotación: {log_max_bytes / (1024*1024):.1f}MB, {log_backup_count} backups")


def register_error_handlers(app: Flask) -> None:
    """Registra handlers globales de errores."""
    
    from flask import jsonify, request
    
    # Helper para agregar headers CORS a respuestas de error
    def add_cors_headers(response):
        """Agrega headers CORS a una respuesta."""
        origin = request.headers.get('Origin')
        if origin:
            dev_origins = [
                "http://192.168.0.11:5178",
                "http://192.168.0.11:5179",
                "http://192.168.0.11:5379",
                "http://localhost:5173",
                "http://localhost:5178",
                "http://localhost:5179",
                "http://localhost:5379"
            ]
            if origin in dev_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Project-ID'
                response.headers['Access-Control-Expose-Headers'] = 'Content-Type, Authorization'
        return response
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.error(f"❌ 400 Bad Request: {request.method} {request.path}")
        logger.error(f"   Error: {str(error)}")
        logger.error(f"   Headers: {dict(request.headers)}")
        try:
            data = request.get_json()
            logger.error(f"   JSON Data: {data}")
        except:
            logger.error(f"   Raw Data: {request.get_data(as_text=True)}")
        response = jsonify({'error': 'Bad Request', 'message': str(error)})
        return add_cors_headers(response), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        response = jsonify({'error': 'Unauthorized', 'message': 'Authentication required'})
        return add_cors_headers(response), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        response = jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'})
        return add_cors_headers(response), 403
    
    @app.errorhandler(404)
    def not_found(error):
        response = jsonify({'error': 'Not Found', 'message': 'Resource not found'})
        return add_cors_headers(response), 404
    
    @app.errorhandler(429)
    def rate_limit_handler(error):
        """Maneja errores de rate limiting con headers CORS."""
        response = jsonify({
            'error': 'Too Many Requests',
            'message': 'Rate limit exceeded. Please try again later.'
        })
        return add_cors_headers(response), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}", exc_info=True)
        response = jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred'})
        return add_cors_headers(response), 500
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'version': '3.0.0',
            'environment': app.config['ENV']
        })


if __name__ == '__main__':
    import os
    
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    
    # Solo para desarrollo (usar gunicorn en producción)
    if env == 'development':
        # Usar socketio.run() para WebSocket support
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=True,
            allow_unsafe_werkzeug=True
        )


