"""
Authentication API
==================

Endpoints para autenticación y gestión de usuarios.

Endpoints:
- POST /api/v1/auth/register - Registrar usuario
- POST /api/v1/auth/login - Login
- POST /api/v1/auth/refresh - Refresh token
- POST /api/v1/auth/logout - Logout
- GET /api/v1/auth/me - Info del usuario actual
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
import logging

from models import db, User, AuditLog

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Registra un nuevo usuario."""
    data = request.get_json()
    
    # Validar datos
    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verificar si ya existe
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    # Crear usuario
    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'analyst')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    logger.info(f"Usuario registrado: {user.username}")
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login de usuario."""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    
    # Buscar usuario - Usar consulta SQL directa como workaround
    from models import db
    from sqlalchemy import text
    import bcrypt
    
    # Consulta directa para evitar problemas con el ORM
    result = db.session.execute(
        text('SELECT id, username, email, password_hash, role, is_active, is_verified FROM users WHERE username = :username'),
        {'username': username}
    ).fetchone()
    
    password_valid = False
    user_id = None
    is_active = False
    
    if result:
        user_id = result[0]
        password_hash = result[3]
        is_active = bool(result[5])
        # Verificar contraseña directamente con bcrypt
        try:
            password_valid = bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
            logger.debug(f"Password check para {username}: {password_valid}")
        except Exception as e:
            logger.error(f"Error verificando password: {e}")
            password_valid = False
    else:
        logger.warning(f"Usuario '{username}' no encontrado en la base de datos")
    
    if not result or not password_valid:
        # Log intento fallido
        try:
            AuditLog(
                user_id=user_id,
                action='login_failed',
                details={'username': username},
                ip_address=request.remote_addr,
                success=False
            )
            db.session.commit()
        except:
            pass
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not is_active:
        return jsonify({'error': 'Account is disabled'}), 403
    
    # Generar tokens
    access_token = create_access_token(identity=str(user_id))
    refresh_token = create_refresh_token(identity=str(user_id))
    
    # Actualizar last_login
    from datetime import datetime
    try:
        db.session.execute(
            text('UPDATE users SET last_login = :now WHERE id = :user_id'),
            {'now': datetime.utcnow(), 'user_id': user_id}
        )
        # Log exitoso
        audit = AuditLog(
            user_id=user_id,
            action='login_success',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string if request.user_agent else None,
            success=True
        )
        db.session.add(audit)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error actualizando login: {e}")
    
    logger.info(f"Login exitoso: {result[1]}")
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user_id,
            'username': result[1],
            'email': result[2],
            'role': result[4],
            'is_active': is_active,
            'is_verified': bool(result[6])
        }
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh del access token."""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({'access_token': access_token}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout del usuario."""
    current_user_id = get_jwt_identity()
    
    # Log logout
    audit = AuditLog(
        user_id=current_user_id,
        action='logout',
        ip_address=request.remote_addr,
        success=True
    )
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obtiene información del usuario actual."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200



