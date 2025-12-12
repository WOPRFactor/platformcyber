"""
Unit Tests for ReportRepository
================================

Tests para el repositorio de reportes con funcionalidades extendidas
para el módulo de reportería V2.
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile

from repositories.report_repository import ReportRepository
from models import Report, db


class TestReportRepository:
    """Tests para ReportRepository."""
    
    @pytest.fixture
    def temp_pdf(self):
        """Crea un archivo PDF temporal para testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write('Mock PDF content for testing')
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
    
    def test_create_report_minimal(self, app, db):
        """Test crear un reporte con campos mínimos."""
        repo = ReportRepository()
        
        report = repo.create(
            title="Test Report",
            report_type="technical",
            format="pdf",
            workspace_id=1,
            created_by=1
        )
        
        assert report.id is not None
        assert report.title == "Test Report"
        assert report.report_type == "technical"
        assert report.format == "pdf"
        assert report.status == "pending"
        assert report.version == 1
        assert report.is_latest is True
    
    def test_create_report_full(self, app, db, temp_pdf):
        """Test crear un reporte con todos los campos."""
        repo = ReportRepository()
        
        report = repo.create(
            title="Complete Test Report",
            report_type="technical",
            format="pdf",
            workspace_id=1,
            created_by=1,
            file_path=temp_pdf,
            file_size=1024,
            total_findings=50,
            critical_count=5,
            high_count=10,
            medium_count=20,
            low_count=10,
            info_count=5,
            risk_score=7.5,
            files_processed=10,
            tools_used=['nmap', 'nuclei', 'nikto'],
            generation_time_seconds=2.5
        )
        
        assert report.id is not None
        assert report.file_path == temp_pdf
        assert report.file_hash is not None  # Hash se calcula automáticamente
        assert report.total_findings == 50
        assert report.critical_count == 5
        assert report.risk_score == 7.5
        assert report.tools_used == ['nmap', 'nuclei', 'nikto']
        assert report.generation_time_seconds == 2.5
        assert report.status == "completed"  # Cambia automáticamente cuando hay file_path
        assert report.generated_at is not None
    
    def test_find_by_id(self, app, db):
        """Test buscar reporte por ID."""
        repo = ReportRepository()
        
        # Crear reporte
        created = repo.create(
            title="Find Test",
            report_type="technical",
            format="pdf",
            workspace_id=1,
            created_by=1
        )
        
        # Buscar
        found = repo.find_by_id(created.id)
        
        assert found is not None
        assert found.id == created.id
        assert found.title == "Find Test"
    
    def test_find_by_id_not_found(self, app, db):
        """Test buscar reporte inexistente."""
        repo = ReportRepository()
        
        found = repo.find_by_id(99999)
        
        assert found is None
    
    def test_find_by_workspace(self, app, db):
        """Test buscar reportes por workspace."""
        repo = ReportRepository()
        
        # Contar reportes existentes antes de crear nuevos
        existing_reports = repo.find_by_workspace(1)
        initial_count = len(existing_reports)
        
        # Crear reportes en diferentes workspaces
        repo.create(title="Report 1", report_type="technical", format="pdf", workspace_id=1, created_by=1)
        repo.create(title="Report 2", report_type="technical", format="pdf", workspace_id=1, created_by=1)
        repo.create(title="Report 3", report_type="technical", format="pdf", workspace_id=2, created_by=1)
        
        # Buscar workspace 1
        reports = repo.find_by_workspace(1)
        
        # Verificar que se agregaron exactamente 2 reportes al workspace 1
        assert len(reports) == initial_count + 2
        assert all(r.workspace_id == 1 for r in reports)
    
    def test_find_by_workspace_with_limit(self, app, db):
        """Test buscar reportes con límite."""
        repo = ReportRepository()
        
        # Crear 10 reportes
        for i in range(10):
            repo.create(
                title=f"Report {i}",
                report_type="technical",
                format="pdf",
                workspace_id=1,
                created_by=1
            )
        
        # Buscar con límite
        reports = repo.find_by_workspace(1, limit=5)
        
        assert len(reports) == 5
    
    def test_find_latest_by_type(self, app, db, temp_pdf):
        """Test buscar reporte más reciente por tipo."""
        repo = ReportRepository()
        
        # Crear reportes de diferentes tipos
        repo.create(
            title="Old Technical",
            report_type="technical",
            format="pdf",
            workspace_id=1,
            created_by=1,
            file_path=temp_pdf
        )
        
        repo.create(
            title="New Technical",
            report_type="technical",
            format="pdf",
            workspace_id=1,
            created_by=1,
            file_path=temp_pdf
        )
        
        repo.create(
            title="Executive",
            report_type="executive",
            format="pdf",
            workspace_id=1,
            created_by=1,
            file_path=temp_pdf
        )
        
        # Buscar más reciente de tipo technical
        latest = repo.find_latest_by_type(1, "technical")
        
        assert latest is not None
        assert latest.title == "New Technical"
        assert latest.report_type == "technical"
    
    def test_update_status(self, app, db):
        """Test actualizar estado del reporte."""
        repo = ReportRepository()
        
        # Crear reporte
        report = repo.create(
            title="Status Test",
            report_type="technical",
            format="pdf",
            workspace_id=1,
            created_by=1
        )
        
        # Actualizar estado
        success = repo.update_status(report.id, "generating")
        
        assert success is True
        
        # Verificar
        updated = repo.find_by_id(report.id)
        assert updated.status == "generating"
    
    def test_update_status_with_error(self, app, db):
        """Test actualizar estado con mensaje de error."""
        repo = ReportRepository()
        
        report = repo.create(
            title="Error Test",
            report_type="technical",
            format="pdf",
            workspace_id=1,
            created_by=1
        )
        
        success = repo.update_status(
            report.id,
            "failed",
            error_message="Test error message"
        )
        
        assert success is True
        
        updated = repo.find_by_id(report.id)
        assert updated.status == "failed"
        assert updated.error_message == "Test error message"
    
    def test_delete_report(self, app, db):
        """Test eliminar reporte."""
        repo = ReportRepository()
        
        report = repo.create(
            title="Delete Test",
            report_type="technical",
            format="pdf",
            workspace_id=1,
            created_by=1
        )
        
        report_id = report.id
        
        # Eliminar
        success = repo.delete(report_id, delete_file=False)
        
        assert success is True
        assert repo.find_by_id(report_id) is None
    
    def test_delete_report_with_file(self, app, db, temp_pdf):
        """Test eliminar reporte y archivo físico."""
        repo = ReportRepository()
        
        report = repo.create(
            title="Delete File Test",
            report_type="technical",
            format="pdf",
            workspace_id=1,
            created_by=1,
            file_path=temp_pdf
        )
        
        # Verificar que el archivo existe
        assert Path(temp_pdf).exists()
        
        # Eliminar con archivo
        success = repo.delete(report.id, delete_file=True)
        
        assert success is True
        assert not Path(temp_pdf).exists()
    
    def test_calculate_file_hash(self, app, db, temp_pdf):
        """Test cálculo de hash del archivo."""
        repo = ReportRepository()
        
        report = repo.create(
            title="Hash Test",
            report_type="technical",
            format="pdf",
            workspace_id=1,
            created_by=1,
            file_path=temp_pdf
        )
        
        # Verificar que el hash se calculó
        assert report.file_hash is not None
        assert len(report.file_hash) == 64  # SHA-256 = 64 caracteres hex
    
    def test_verify_integrity(self, app, db, temp_pdf):
        """Test verificación de integridad."""
        repo = ReportRepository()
        
        report = repo.create(
            title="Integrity Test",
            report_type="technical",
            format="pdf",
            workspace_id=1,
            created_by=1,
            file_path=temp_pdf
        )
        
        # Verificar integridad (debe ser válida)
        assert report.verify_integrity() is True
        
        # Corromper el archivo
        with open(temp_pdf, 'a') as f:
            f.write('corrupted data')
        
        # Verificar integridad (debe fallar)
        assert report.verify_integrity() is False
    
    def test_to_dict(self, app, db):
        """Test serialización a diccionario."""
        repo = ReportRepository()
        
        report = repo.create(
            title="Dict Test",
            report_type="technical",
            format="pdf",
            workspace_id=1,
            created_by=1,
            total_findings=10,
            critical_count=2,
            high_count=3,
            risk_score=5.5
        )
        
        data = report.to_dict()
        
        assert data['id'] == report.id
        assert data['title'] == "Dict Test"
        assert data['total_findings'] == 10
        assert data['severity_counts']['critical'] == 2
        assert data['severity_counts']['high'] == 3
        assert data['risk_score'] == 5.5

