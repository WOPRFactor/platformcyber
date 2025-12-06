"""
Test Reporting Flow (Integration)
==================================

Tests de integración para generación de reportes.
"""

import pytest
from services import ReportingService, VulnerabilityService


class TestReportingFlow:
    """Tests de integración para reportes."""
    
    def test_generate_executive_report(self, db, sample_user, sample_workspace):
        """Test generación de reporte ejecutivo."""
        # Arrange
        reporting_service = ReportingService()
        vuln_service = VulnerabilityService()
        
        # Crear algunas vulnerabilidades
        vuln_service.create_vulnerability(
            title='Critical Issue',
            description='Test',
            severity='critical',
            target='test.com',
            workspace_id=sample_workspace.id
        )
        
        # Act: Generar reporte
        report = reporting_service.generate_executive_report(
            workspace_id=sample_workspace.id,
            user_id=sample_user.id,
            title='Executive Report Test'
        )
        
        # Assert
        assert report['report_id'] is not None
        assert report['type'] == 'executive'
        assert report['format'] == 'html'
        assert report['critical_vulns_count'] >= 1
    
    def test_generate_technical_report(self, db, sample_user, sample_workspace):
        """Test generación de reporte técnico."""
        reporting_service = ReportingService()
        
        # Act
        report = reporting_service.generate_technical_report(
            workspace_id=sample_workspace.id,
            user_id=sample_user.id,
            title='Technical Report Test'
        )
        
        # Assert
        assert report['report_id'] is not None
        assert report['type'] == 'technical'
        assert report['format'] == 'html'
    
    def test_export_json(self, db, sample_user, sample_workspace):
        """Test exportación a JSON."""
        reporting_service = ReportingService()
        vuln_service = VulnerabilityService()
        
        # Crear datos
        vuln_service.create_vulnerability(
            title='Test Vuln',
            description='Test',
            severity='medium',
            target='test.com',
            workspace_id=sample_workspace.id
        )
        
        # Act: Exportar
        data = reporting_service.export_json(
            workspace_id=sample_workspace.id,
            user_id=sample_user.id
        )
        
        # Assert
        assert 'workspace' in data
        assert 'vulnerabilities' in data
        assert 'scans' in data
        assert len(data['vulnerabilities']) == 1



