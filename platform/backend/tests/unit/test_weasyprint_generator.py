"""
Unit Tests for WeasyPrintPDFGenerator
======================================

Tests para el generador de PDFs usando WeasyPrint.
"""

import pytest
from pathlib import Path
import tempfile
import os

from services.reporting.generators.pdf_generator_weasy import WeasyPrintPDFGenerator
from services.reporting.parsers.base_parser import ParsedFinding


class TestWeasyPrintPDFGenerator:
    """Tests para WeasyPrintPDFGenerator."""
    
    @pytest.fixture
    def generator(self):
        """Crea una instancia del generador."""
        return WeasyPrintPDFGenerator()
    
    @pytest.fixture
    def sample_findings(self):
        """Crea findings de ejemplo para testing."""
        return [
            ParsedFinding(
                title="SQL Injection en Login",
                severity="critical",
                description="Vulnerabilidad de inyección SQL en el formulario de login",
                category="vulnerability",
                affected_target="https://example.com/login",
                evidence="' OR '1'='1' -- bypasses authentication",
                remediation="Usar prepared statements o parametrized queries",
                cve_id="CVE-2024-12345",
                references=["https://cwe.mitre.org/data/definitions/89.html"]
            ),
            ParsedFinding(
                title="Cross-Site Scripting (XSS)",
                severity="high",
                description="XSS reflejado en parámetro de búsqueda",
                category="vulnerability",
                affected_target="https://example.com/search",
                evidence="<script>alert('XSS')</script>",
                remediation="Sanitizar y escapar inputs de usuario"
            ),
            ParsedFinding(
                title="Puerto SSH Abierto",
                severity="low",
                description="Puerto 22 expuesto públicamente",
                category="port_scan",
                affected_target="192.168.1.100:22",
                remediation="Limitar acceso SSH solo a IPs autorizadas"
            ),
            ParsedFinding(
                title="Información del Servidor",
                severity="info",
                description="Banner del servidor revela versión",
                category="information_disclosure",
                affected_target="192.168.1.100:80"
            )
        ]
    
    @pytest.fixture
    def sample_statistics(self):
        """Estadísticas de ejemplo."""
        return {
            'total_findings': 4,
            'total_files': 5,
            'targets': ['example.com', '192.168.1.100'],
            'by_category': {
                'vulnerability': 2,
                'port_scan': 1,
                'information_disclosure': 1
            },
            'by_severity': {
                'critical': 1,
                'high': 1,
                'medium': 0,
                'low': 1,
                'info': 1
            }
        }
    
    @pytest.fixture
    def sample_risk_metrics(self):
        """Métricas de riesgo de ejemplo."""
        return {
            'risk_score': 7.8,
            'risk_level': 'high',
            'severity_distribution': {
                'critical': 1,
                'high': 1,
                'medium': 0,
                'low': 1,
                'info': 1
            }
        }
    
    @pytest.fixture
    def sample_metadata(self):
        """Metadata de ejemplo."""
        return {
            'workspace': {
                'name': 'Test Workspace',
                'description': 'Workspace de testing'
            },
            'tools_used': ['nmap', 'nuclei', 'nikto'],
            'generation_time': 2.5
        }
    
    @pytest.fixture
    def temp_output_path(self):
        """Crea un path temporal para el PDF."""
        fd, path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        yield Path(path)
        # Cleanup
        Path(path).unlink(missing_ok=True)
    
    def test_generator_initialization(self, generator):
        """Test que el generador se inicializa correctamente."""
        assert generator is not None
        assert generator.jinja_env is not None
    
    def test_generate_technical_report(
        self,
        generator,
        temp_output_path,
        sample_findings,
        sample_statistics,
        sample_risk_metrics,
        sample_metadata
    ):
        """Test generar reporte técnico completo."""
        result = generator.generate_technical_report(
            output_path=temp_output_path,
            workspace_name="Test Workspace",
            findings=sample_findings,
            statistics=sample_statistics,
            risk_metrics=sample_risk_metrics,
            metadata=sample_metadata
        )
        
        # Verificar que se generó el archivo
        assert result == temp_output_path
        assert temp_output_path.exists()
        assert temp_output_path.stat().st_size > 0
        
        # Verificar que es un PDF válido (comienza con %PDF)
        with open(temp_output_path, 'rb') as f:
            header = f.read(4)
            assert header == b'%PDF'
    
    def test_generate_with_empty_findings(
        self,
        generator,
        temp_output_path,
        sample_statistics,
        sample_risk_metrics,
        sample_metadata
    ):
        """Test generar reporte sin findings."""
        result = generator.generate_technical_report(
            output_path=temp_output_path,
            workspace_name="Empty Workspace",
            findings=[],
            statistics={'total_findings': 0, 'total_files': 0, 'targets': []},
            risk_metrics={'risk_score': 0, 'risk_level': 'low', 'severity_distribution': {}},
            metadata=sample_metadata
        )
        
        assert result.exists()
        assert result.stat().st_size > 0
    
    def test_generate_interface_method(
        self,
        generator,
        temp_output_path,
        sample_findings,
        sample_statistics,
        sample_risk_metrics,
        sample_metadata
    ):
        """Test método generate() para compatibilidad."""
        result = generator.generate(
            findings=sample_findings,
            statistics=sample_statistics,
            risk_metrics=sample_risk_metrics,
            metadata=sample_metadata,
            output_path=temp_output_path
        )
        
        assert result.exists()
        assert result.stat().st_size > 0
    
    def test_prepare_template_data(
        self,
        generator,
        sample_findings,
        sample_statistics,
        sample_risk_metrics,
        sample_metadata
    ):
        """Test preparación de datos para template."""
        data = generator._prepare_template_data(
            workspace_name="Test Workspace",
            findings=sample_findings,
            statistics=sample_statistics,
            risk_metrics=sample_risk_metrics,
            metadata=sample_metadata
        )
        
        # Verificar estructura de datos
        assert 'workspace_name' in data
        assert 'report_date' in data
        assert 'report_time' in data
        assert 'findings' in data
        assert 'findings_by_category' in data
        assert 'critical_findings' in data
        assert 'total_findings' in data
        assert 'risk_score' in data
        assert 'tools_used' in data
        
        # Verificar que findings se organizan por categoría
        assert 'vulnerability' in data['findings_by_category']
        assert 'port_scan' in data['findings_by_category']
        
        # Verificar que critical_findings está filtrado
        assert len(data['critical_findings']) == 2  # critical + high
        assert all(f.severity in ['critical', 'high'] for f in data['critical_findings'])
    
    def test_findings_sorted_by_severity(
        self,
        generator,
        sample_findings,
        sample_statistics,
        sample_risk_metrics,
        sample_metadata
    ):
        """Test que findings se ordenan por severidad."""
        data = generator._prepare_template_data(
            workspace_name="Test",
            findings=sample_findings,
            statistics=sample_statistics,
            risk_metrics=sample_risk_metrics,
            metadata=sample_metadata
        )
        
        # Verificar orden en findings_by_category
        for category, findings in data['findings_by_category'].items():
            # Verificar que critical viene antes que high, etc.
            severities = [f.severity for f in findings]
            severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
            severity_values = [severity_order.get(s, 999) for s in severities]
            assert severity_values == sorted(severity_values)
    
    def test_get_pdf_stylesheet(self, generator):
        """Test que se genera el stylesheet CSS."""
        css = generator._get_pdf_stylesheet()
        
        assert css is not None
        # Verificar que es un objeto CSS de WeasyPrint
        from weasyprint import CSS
        assert isinstance(css, CSS)
    
    def test_generate_with_long_findings_list(
        self,
        generator,
        temp_output_path,
        sample_statistics,
        sample_risk_metrics,
        sample_metadata
    ):
        """Test generar reporte con muchos findings."""
        # Crear 100 findings
        many_findings = [
            ParsedFinding(
                title=f"Finding {i}",
                severity="medium",
                description=f"Description for finding {i}",
                category="test",
                affected_target=f"target-{i}.example.com"
            )
            for i in range(100)
        ]
        
        result = generator.generate_technical_report(
            output_path=temp_output_path,
            workspace_name="Large Workspace",
            findings=many_findings,
            statistics={'total_findings': 100, 'total_files': 10, 'targets': []},
            risk_metrics={'risk_score': 5.0, 'risk_level': 'medium', 'severity_distribution': {'medium': 100}},
            metadata=sample_metadata
        )
        
        assert result.exists()
        # PDF debería ser más grande con más findings
        assert result.stat().st_size > 10000  # Al menos 10KB
    
    def test_generate_with_special_characters(
        self,
        generator,
        temp_output_path,
        sample_statistics,
        sample_risk_metrics,
        sample_metadata
    ):
        """Test generar reporte con caracteres especiales."""
        special_findings = [
            ParsedFinding(
                title="Finding with <script>alert('XSS')</script>",
                severity="high",
                description="Description with & < > \" ' special chars",
                category="test",
                affected_target="https://example.com/test?param=<script>"
            )
        ]
        
        result = generator.generate_technical_report(
            output_path=temp_output_path,
            workspace_name="Test <Special> Workspace",
            findings=special_findings,
            statistics={'total_findings': 1, 'total_files': 1, 'targets': []},
            risk_metrics={'risk_score': 6.0, 'risk_level': 'high', 'severity_distribution': {'high': 1}},
            metadata=sample_metadata
        )
        
        # Debería manejar caracteres especiales sin errores
        assert result.exists()
        assert result.stat().st_size > 0



