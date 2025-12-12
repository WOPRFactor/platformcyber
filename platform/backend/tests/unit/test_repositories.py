"""
Test Repositories
=================

Tests para repositories (acceso a datos).
"""

import pytest
from repositories import UserRepository, ScanRepository, VulnerabilityRepository


class TestUserRepository:
    """Tests para UserRepository."""
    
    def test_create_user(self, db):
        """Test creación de usuario."""
        user = UserRepository.create(
            username='newuser',
            email='newuser@example.com',
            password='password123',
            role='analyst'
        )
        
        assert user.id is not None
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'
        assert user.role == 'analyst'
        assert user.check_password('password123')
    
    def test_find_by_username(self, db, sample_user):
        """Test búsqueda por username."""
        user = UserRepository.find_by_username('testuser')
        
        assert user is not None
        assert user.username == 'testuser'
    
    def test_find_by_email(self, db, sample_user):
        """Test búsqueda por email."""
        user = UserRepository.find_by_email('test@example.com')
        
        assert user is not None
        assert user.email == 'test@example.com'
    
    def test_user_exists(self, db, sample_user):
        """Test verificación de existencia."""
        assert UserRepository.exists(username='testuser')
        assert UserRepository.exists(email='test@example.com')
        assert not UserRepository.exists(username='nonexistent')


class TestScanRepository:
    """Tests para ScanRepository."""
    
    def test_create_scan(self, db, sample_user, sample_workspace):
        """Test creación de escaneo."""
        scan = ScanRepository.create(
            scan_type='port_scan',
            target='192.168.1.1',
            workspace_id=sample_workspace.id,
            user_id=sample_user.id,
            options={'tool': 'nmap'}
        )
        
        assert scan.id is not None
        assert scan.scan_type == 'port_scan'
        assert scan.target == '192.168.1.1'
        assert scan.status == 'pending'
    
    def test_update_status(self, db, sample_user, sample_workspace):
        """Test actualización de estado."""
        scan = ScanRepository.create(
            scan_type='port_scan',
            target='192.168.1.1',
            workspace_id=sample_workspace.id,
            user_id=sample_user.id
        )
        
        updated = ScanRepository.update_status(scan, 'running')
        
        assert updated.status == 'running'
        assert updated.started_at is not None
    
    def test_update_progress(self, db, sample_user, sample_workspace):
        """Test actualización de progreso."""
        scan = ScanRepository.create(
            scan_type='port_scan',
            target='192.168.1.1',
            workspace_id=sample_workspace.id,
            user_id=sample_user.id
        )
        
        updated = ScanRepository.update_progress(scan, 50, 'Output...')
        
        assert updated.progress == 50
        assert updated.output == 'Output...'


class TestVulnerabilityRepository:
    """Tests para VulnerabilityRepository."""
    
    def test_create_vulnerability(self, db, sample_workspace):
        """Test creación de vulnerabilidad."""
        vuln = VulnerabilityRepository.create(
            title='SQL Injection',
            description='SQL injection found',
            severity='high',
            target='https://example.com',
            workspace_id=sample_workspace.id,
            cve_id='CVE-2024-1234'
        )
        
        assert vuln.id is not None
        assert vuln.title == 'SQL Injection'
        assert vuln.severity == 'high'
        assert vuln.status == 'open'
    
    def test_find_by_severity(self, db, sample_workspace):
        """Test búsqueda por severidad."""
        # Crear vulnerabilidades
        VulnerabilityRepository.create(
            title='Critical Vuln',
            description='Test',
            severity='critical',
            target='test.com',
            workspace_id=sample_workspace.id
        )
        VulnerabilityRepository.create(
            title='Low Vuln',
            description='Test',
            severity='low',
            target='test.com',
            workspace_id=sample_workspace.id
        )
        
        # Buscar solo critical
        vulns = VulnerabilityRepository.find_by_severity(
            sample_workspace.id,
            ['critical']
        )
        
        assert len(vulns) == 1
        assert vulns[0].severity == 'critical'
    
    def test_get_stats(self, db, sample_workspace):
        """Test estadísticas de vulnerabilidades."""
        # Crear vulnerabilidades
        VulnerabilityRepository.create(
            title='Vuln 1',
            description='Test',
            severity='critical',
            target='test.com',
            workspace_id=sample_workspace.id
        )
        VulnerabilityRepository.create(
            title='Vuln 2',
            description='Test',
            severity='high',
            target='test.com',
            workspace_id=sample_workspace.id
        )
        
        stats = VulnerabilityRepository.get_stats(sample_workspace.id)
        
        assert stats['total'] == 2
        assert 'by_severity' in stats
        assert 'by_status' in stats



