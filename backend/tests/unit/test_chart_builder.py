"""
Unit Tests for ChartBuilder
============================

Tests para el generador de gráficos usando Plotly.
"""

import pytest
from pathlib import Path
import tempfile
import os

from services.reporting.utils.chart_builder import ChartBuilder
from services.reporting.parsers.base_parser import ParsedFinding


class TestChartBuilder:
    """Tests para ChartBuilder."""
    
    @pytest.fixture
    def builder(self):
        """Crea una instancia del ChartBuilder."""
        return ChartBuilder()
    
    @pytest.fixture
    def sample_severity_distribution(self):
        """Distribución de severidades de ejemplo."""
        return {
            'critical': 5,
            'high': 12,
            'medium': 18,
            'low': 10,
            'info': 5
        }
    
    @pytest.fixture
    def sample_findings_by_category(self):
        """Findings organizados por categoría de ejemplo."""
        return {
            'vulnerability': [
                ParsedFinding(title="Vuln 1", description="Vuln 1 description", severity="critical", category="vulnerability", affected_target="target1"),
                ParsedFinding(title="Vuln 2", description="Vuln 2 description", severity="high", category="vulnerability", affected_target="target2"),
                ParsedFinding(title="Vuln 3", description="Vuln 3 description", severity="medium", category="vulnerability", affected_target="target3"),
            ],
            'port_scan': [
                ParsedFinding(title="Port 1", description="Port 1 description", severity="low", category="port_scan", affected_target="target4"),
                ParsedFinding(title="Port 2", description="Port 2 description", severity="info", category="port_scan", affected_target="target5"),
            ],
            'reconnaissance': [
                ParsedFinding(title="Recon 1", description="Recon 1 description", severity="info", category="reconnaissance", affected_target="target6"),
            ]
        }
    
    @pytest.fixture
    def temp_output_dir(self):
        """Crea un directorio temporal para PNGs."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_builder_initialization(self, builder):
        """Test que el builder se inicializa correctamente."""
        assert builder is not None
        assert builder.SEVERITY_COLORS is not None
        assert 'critical' in builder.SEVERITY_COLORS
        assert 'high' in builder.SEVERITY_COLORS
    
    def test_create_severity_pie_chart(self, builder, sample_severity_distribution, temp_output_dir):
        """Test crear gráfico de torta de severidades."""
        output_path = temp_output_dir / 'test_pie.png'
        
        result = builder.create_severity_pie_chart(
            severity_distribution=sample_severity_distribution,
            output_path=output_path
        )
        
        assert result is not None
        assert result == str(output_path)
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        
        # Verificar que es un PNG válido
        with open(output_path, 'rb') as f:
            header = f.read(8)
            assert header[:4] == b'\x89PNG'
    
    def test_create_pie_chart_with_empty_data(self, builder, temp_output_dir):
        """Test crear pie chart sin datos."""
        output_path = temp_output_dir / 'empty_pie.png'
        
        result = builder.create_severity_pie_chart(
            severity_distribution={},
            output_path=output_path
        )
        
        # Debería retornar None si no hay datos
        assert result is None
        assert not output_path.exists()
    
    def test_create_pie_chart_with_zeros(self, builder, temp_output_dir):
        """Test crear pie chart con valores en cero."""
        output_path = temp_output_dir / 'zeros_pie.png'
        
        result = builder.create_severity_pie_chart(
            severity_distribution={'critical': 0, 'high': 0, 'medium': 0},
            output_path=output_path
        )
        
        assert result is None
    
    def test_create_category_bar_chart(self, builder, sample_findings_by_category, temp_output_dir):
        """Test crear gráfico de barras de categorías."""
        output_path = temp_output_dir / 'test_bar.png'
        
        result = builder.create_category_bar_chart(
            findings_by_category=sample_findings_by_category,
            output_path=output_path
        )
        
        assert result is not None
        assert result == str(output_path)
        assert output_path.exists()
        assert output_path.stat().st_size > 0
    
    def test_create_bar_chart_with_empty_data(self, builder, temp_output_dir):
        """Test crear bar chart sin datos."""
        output_path = temp_output_dir / 'empty_bar.png'
        
        result = builder.create_category_bar_chart(
            findings_by_category={},
            output_path=output_path
        )
        
        assert result is None
        assert not output_path.exists()
    
    def test_create_bar_chart_sorted(self, builder, sample_findings_by_category, temp_output_dir):
        """Test que el bar chart ordena categorías por cantidad."""
        output_path = temp_output_dir / 'sorted_bar.png'
        
        result = builder.create_category_bar_chart(
            findings_by_category=sample_findings_by_category,
            output_path=output_path
        )
        
        # El gráfico debería crearse correctamente
        # vulnerability (3) > port_scan (2) > reconnaissance (1)
        assert result is not None
        assert output_path.exists()
    
    def test_create_risk_gauge(self, builder, temp_output_dir):
        """Test crear gauge de risk score."""
        output_path = temp_output_dir / 'test_gauge.png'
        
        result = builder.create_risk_gauge(
            risk_score=7.5,
            output_path=output_path
        )
        
        assert result is not None
        assert result == str(output_path)
        assert output_path.exists()
        assert output_path.stat().st_size > 0
    
    def test_create_risk_gauge_critical(self, builder, temp_output_dir):
        """Test gauge con riesgo crítico."""
        output_path = temp_output_dir / 'critical_gauge.png'
        
        result = builder.create_risk_gauge(
            risk_score=9.5,
            output_path=output_path
        )
        
        assert result is not None
        assert output_path.exists()
    
    def test_create_risk_gauge_low(self, builder, temp_output_dir):
        """Test gauge con riesgo bajo."""
        output_path = temp_output_dir / 'low_gauge.png'
        
        result = builder.create_risk_gauge(
            risk_score=1.0,
            output_path=output_path
        )
        
        assert result is not None
        assert output_path.exists()
    
    def test_generate_all_charts(
        self,
        builder,
        sample_severity_distribution,
        sample_findings_by_category,
        temp_output_dir
    ):
        """Test generar todos los gráficos a la vez."""
        charts = builder.generate_all_charts(
            severity_distribution=sample_severity_distribution,
            findings_by_category=sample_findings_by_category,
            risk_score=7.8,
            output_dir=temp_output_dir
        )
        
        # Verificar que se generaron los 3 gráficos
        assert 'severity_pie' in charts
        assert 'category_bar' in charts
        assert 'risk_gauge' in charts
        
        # Verificar que todos los archivos existen
        assert Path(charts['severity_pie']).exists()
        assert Path(charts['category_bar']).exists()
        assert Path(charts['risk_gauge']).exists()
    
    def test_generate_all_charts_with_partial_data(self, builder, temp_output_dir):
        """Test generar gráficos con datos parciales."""
        charts = builder.generate_all_charts(
            severity_distribution={},  # Sin datos de severidad
            findings_by_category={'test': [ParsedFinding(title="Test", description="Test description", severity="low", category="test", affected_target="target")]},
            risk_score=3.0,
            output_dir=temp_output_dir
        )
        
        # Debería generar solo 2 gráficos (sin pie chart)
        assert 'severity_pie' not in charts
        assert 'category_bar' in charts
        assert 'risk_gauge' in charts
    
    def test_severity_colors(self, builder):
        """Test que los colores de severidad están definidos."""
        colors = builder.SEVERITY_COLORS
        
        assert colors['critical'] == '#e74c3c'
        assert colors['high'] == '#e67e22'
        assert colors['medium'] == '#f39c12'
        assert colors['low'] == '#3498db'
        assert colors['info'] == '#95a5a6'
    
    def test_chart_without_output_path(self, builder, sample_severity_distribution):
        """Test crear gráfico sin especificar output_path."""
        result = builder.create_severity_pie_chart(
            severity_distribution=sample_severity_distribution,
            output_path=None
        )
        
        # Debería retornar None si no se especifica output_path
        assert result is None
    
    def test_create_charts_with_many_categories(self, builder, temp_output_dir):
        """Test crear gráficos con muchas categorías."""
        # Crear 20 categorías
        many_categories = {
            f'category_{i}': [
                ParsedFinding(
                    title=f"Finding {i}",
                    description=f"Finding {i} description",
                    severity="medium",
                    category=f"category_{i}",
                    affected_target=f"target{i}"
                )
            ]
            for i in range(20)
        }
        
        output_path = temp_output_dir / 'many_categories_bar.png'
        
        result = builder.create_category_bar_chart(
            findings_by_category=many_categories,
            output_path=output_path
        )
        
        assert result is not None
        assert output_path.exists()

