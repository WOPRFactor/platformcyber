"""
Pytest Configuration & Shared Fixtures
=======================================

Fixtures compartidas para todos los tests.
"""

import pytest
import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db as _db
from models.user import User
from models.workspace import Workspace
from models.scan import Scan
from repositories import UserRepository, WorkspaceRepository, ScanRepository


@pytest.fixture(scope='session')
def app():
    """
    Fixture de aplicación Flask para toda la sesión de tests.
    
    Returns:
        Flask app configurada para testing
    """
    app = create_app('testing')
    
    # Push application context
    ctx = app.app_context()
    ctx.push()
    
    yield app
    
    ctx.pop()


@pytest.fixture(scope='session')
def db(app):
    """
    Fixture de base de datos para toda la sesión.
    
    Args:
        app: Flask app fixture
    
    Returns:
        SQLAlchemy db instance
    """
    # Crear todas las tablas
    _db.create_all()
    
    yield _db
    
    # Cleanup
    _db.drop_all()


@pytest.fixture(scope='function')
def session(db):
    """
    Fixture de sesión de DB para cada test (con rollback automático).
    
    Args:
        db: Database fixture
    
    Returns:
        DB session
    """
    connection = db.engine.connect()
    transaction = connection.begin()
    
    session = db.create_scoped_session(
        options={'bind': connection, 'binds': {}}
    )
    
    db.session = session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def client(app):
    """
    Fixture de cliente Flask para hacer requests HTTP.
    
    Args:
        app: Flask app fixture
    
    Returns:
        Flask test client
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Fixture de CLI runner para comandos Flask.
    
    Args:
        app: Flask app fixture
    
    Returns:
        Flask CLI test runner
    """
    return app.test_cli_runner()


# ============================================
# USER FIXTURES
# ============================================

@pytest.fixture
def user_data():
    """Datos de usuario para tests."""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'role': 'pentester'
    }


@pytest.fixture
def admin_user(session):
    """
    Crea un usuario admin para tests.
    
    Args:
        session: DB session fixture
    
    Returns:
        User: Admin user
    """
    user_repo = UserRepository()
    
    user = user_repo.create(
        username='admin',
        email='admin@example.com',
        password='Admin123!@#',
        role='admin'
    )
    
    session.commit()
    
    return user


@pytest.fixture
def regular_user(session):
    """
    Crea un usuario regular para tests.
    
    Args:
        session: DB session fixture
    
    Returns:
        User: Regular user
    """
    user_repo = UserRepository()
    
    user = user_repo.create(
        username='pentester1',
        email='pentester@example.com',
        password='Pent123!@#',
        role='pentester'
    )
    
    session.commit()
    
    return user


@pytest.fixture
def auth_headers(client, admin_user):
    """
    Headers de autenticación para requests HTTP.
    
    Args:
        client: Flask test client
        admin_user: Admin user fixture
    
    Returns:
        dict: Headers con JWT token
    """
    # Login para obtener token
    response = client.post('/api/v1/auth/login', json={
        'username': 'admin',
        'password': 'Admin123!@#'
    })
    
    data = response.get_json()
    token = data.get('access_token')
    
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


# ============================================
# WORKSPACE FIXTURES
# ============================================

@pytest.fixture
def workspace(session, admin_user):
    """
    Crea un workspace para tests.
    
    Args:
        session: DB session fixture
        admin_user: Admin user fixture
    
    Returns:
        Workspace: Test workspace
    """
    workspace_repo = WorkspaceRepository()
    
    workspace = workspace_repo.create(
        name='Test Workspace',
        description='Workspace for testing',
        owner_id=admin_user.id
    )
    
    session.commit()
    
    return workspace


@pytest.fixture
def workspace_data():
    """Datos de workspace para tests."""
    return {
        'name': 'Test Project',
        'description': 'Test project description',
        'client_name': 'Test Client',
        'client_contact': 'client@example.com'
    }


# ============================================
# SCAN FIXTURES
# ============================================

@pytest.fixture
def scan(session, workspace, admin_user):
    """
    Crea un scan para tests.
    
    Args:
        session: DB session fixture
        workspace: Workspace fixture
        admin_user: Admin user fixture
    
    Returns:
        Scan: Test scan
    """
    scan_repo = ScanRepository()
    
    scan = scan_repo.create(
        scan_type='reconnaissance',
        target='192.168.1.1',
        workspace_id=workspace.id,
        user_id=admin_user.id,
        options={'tool': 'nmap', 'scan_type': 'quick'}
    )
    
    session.commit()
    
    return scan


@pytest.fixture
def scan_data():
    """Datos de scan para tests."""
    return {
        'scan_type': 'reconnaissance',
        'target': '192.168.1.100',
        'options': {
            'tool': 'nmap',
            'scan_type': 'intense',
            'ports': '1-1000'
        }
    }


@pytest.fixture
def completed_scan(session, workspace, admin_user):
    """
    Crea un scan completado para tests.
    
    Args:
        session: DB session fixture
        workspace: Workspace fixture
        admin_user: Admin user fixture
    
    Returns:
        Scan: Completed scan
    """
    scan_repo = ScanRepository()
    
    scan = scan_repo.create(
        scan_type='reconnaissance',
        target='192.168.1.1',
        workspace_id=workspace.id,
        user_id=admin_user.id,
        options={'tool': 'nmap'}
    )
    
    # Marcar como completado
    scan_repo.update_status(scan, 'completed')
    scan.progress = 100
    scan.completed_at = datetime.utcnow()
    
    session.commit()
    
    return scan


# ============================================
# MOCK FIXTURES
# ============================================

@pytest.fixture
def mock_nmap_output():
    """Output de ejemplo de Nmap para tests."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<nmaprun scanner="nmap" version="7.94">
  <host>
    <address addr="192.168.1.1" addrtype="ipv4"/>
    <status state="up"/>
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open"/>
        <service name="ssh" product="OpenSSH" version="8.9p1"/>
      </port>
      <port protocol="tcp" portid="80">
        <state state="open"/>
        <service name="http" product="nginx" version="1.18.0"/>
      </port>
      <port protocol="tcp" portid="443">
        <state state="open"/>
        <service name="https" product="nginx" version="1.18.0"/>
      </port>
    </ports>
  </host>
</nmaprun>'''


@pytest.fixture
def mock_nuclei_output():
    """Output de ejemplo de Nuclei para tests."""
    return '''[2023-11-23 10:00:00] [http-missing-security-headers] [info] https://example.com [X-Frame-Options header missing]
[2023-11-23 10:00:01] [ssl-tls-version] [medium] https://example.com [TLSv1.0 is enabled]
[2023-11-23 10:00:02] [exposed-admin-panel] [high] https://example.com/admin [Admin panel exposed]'''


@pytest.fixture
def mock_sqlmap_output():
    """Output de ejemplo de SQLMap para tests."""
    return '''[10:00:00] [INFO] testing 'MySQL >= 5.0.12 AND time-based blind'
[10:00:01] [INFO] GET parameter 'id' appears to be 'MySQL >= 5.0.12 AND time-based blind' injectable
[10:00:02] [INFO] the back-end DBMS is MySQL
web application technology: PHP 7.4.3, Apache 2.4.41
back-end DBMS: MySQL >= 5.0.12'''


# ============================================
# CELERY FIXTURES
# ============================================

@pytest.fixture
def celery_app():
    """
    Fixture de Celery app para tests.
    
    Returns:
        Celery app configurada para testing
    """
    from celery_app import celery
    
    # Configurar para testing (eager mode)
    celery.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )
    
    return celery


@pytest.fixture
def mock_task_result():
    """Mock de resultado de tarea de Celery."""
    return {
        'task_id': 'test-task-123',
        'state': 'SUCCESS',
        'result': {
            'scan_id': 1,
            'status': 'completed',
            'output_file': '/tmp/test_scan.xml'
        }
    }


# ============================================
# HELPER FUNCTIONS
# ============================================

def create_test_user(session, username='testuser', role='pentester'):
    """
    Helper para crear usuarios en tests.
    
    Args:
        session: DB session
        username: Username
        role: User role
    
    Returns:
        User: Created user
    """
    user_repo = UserRepository()
    user = user_repo.create(
        username=username,
        email=f'{username}@example.com',
        password='Test123!@#',
        role=role
    )
    session.commit()
    return user


def create_test_workspace(session, owner_id, name='Test Workspace'):
    """
    Helper para crear workspaces en tests.
    
    Args:
        session: DB session
        owner_id: Owner user ID
        name: Workspace name
    
    Returns:
        Workspace: Created workspace
    """
    workspace_repo = WorkspaceRepository()
    workspace = workspace_repo.create(
        name=name,
        description='Test workspace',
        owner_id=owner_id
    )
    session.commit()
    return workspace


def create_test_scan(session, workspace_id, user_id, scan_type='reconnaissance'):
    """
    Helper para crear scans en tests.
    
    Args:
        session: DB session
        workspace_id: Workspace ID
        user_id: User ID
        scan_type: Scan type
    
    Returns:
        Scan: Created scan
    """
    scan_repo = ScanRepository()
    scan = scan_repo.create(
        scan_type=scan_type,
        target='192.168.1.1',
        workspace_id=workspace_id,
        user_id=user_id,
        options={'tool': 'nmap'}
    )
    session.commit()
    return scan
