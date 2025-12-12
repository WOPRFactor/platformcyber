"""
Chart Builder
=============

Generador de gráficos para reportes usando Plotly.
Crea visualizaciones profesionales en formato PNG para incluir en PDFs.

Gráficos soportados:
- Pie Chart: Distribución de severidades
- Bar Chart: Hallazgos por categoría
- Gauge: Risk Score visual
"""

import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ChartBuilder:
    """Construye gráficos para reportes usando Plotly."""
    
    # Colores por severidad (consistentes con el CSS)
    SEVERITY_COLORS = {
        'critical': '#e74c3c',
        'high': '#e67e22',
        'medium': '#f39c12',
        'low': '#3498db',
        'info': '#95a5a6'
    }
    
    def create_severity_pie_chart(
        self,
        severity_distribution: Dict[str, int],
        output_path: Optional[Path] = None
    ) -> Optional[str]:
        """
        Crea un gráfico de torta (pie chart) de distribución de severidades.
        
        Args:
            severity_distribution: Dict con contadores por severidad
                Ej: {'critical': 5, 'high': 12, 'medium': 18, 'low': 10, 'info': 5}
            output_path: Ruta donde guardar la imagen PNG (opcional)
            
        Returns:
            str: Path a la imagen PNG si output_path fue especificado, 
                 None si no hay datos o si falla
        """
        try:
            # Filtrar severidades con valores > 0
            labels = []
            values = []
            colors = []
            
            for severity in ['critical', 'high', 'medium', 'low', 'info']:
                count = severity_distribution.get(severity, 0)
                if count > 0:
                    labels.append(severity.capitalize())
                    values.append(count)
                    colors.append(self.SEVERITY_COLORS[severity])
            
            if not values:
                logger.warning("No data for pie chart")
                return None
            
            # Crear gráfico
            fig = go.Figure(data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    marker=dict(colors=colors),
                    textinfo='label+value+percent',
                    textfont=dict(size=14),
                    hole=0.3  # Donut chart
                )
            ])
            
            fig.update_layout(
                title=dict(
                    text="Distribución de Hallazgos por Severidad",
                    font=dict(size=18, color='#2c3e50')
                ),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                ),
                width=600,
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            # Guardar como PNG
            if output_path:
                fig.write_image(str(output_path), format='png')
                logger.info(f"Pie chart saved to: {output_path}")
                return str(output_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating pie chart: {e}", exc_info=True)
            return None
    
    def create_category_bar_chart(
        self,
        findings_by_category: Dict[str, List],
        output_path: Optional[Path] = None
    ) -> Optional[str]:
        """
        Crea un gráfico de barras de hallazgos por categoría.
        
        Args:
            findings_by_category: Dict con findings organizados por categoría
                Ej: {'vulnerability': [finding1, finding2], 'port_scan': [finding3]}
            output_path: Ruta donde guardar la imagen PNG (opcional)
            
        Returns:
            str: Path a la imagen PNG si output_path fue especificado,
                 None si no hay datos o si falla
        """
        try:
            # Preparar datos
            categories = []
            counts = []
            
            for category, findings in findings_by_category.items():
                categories.append(category.replace('_', ' ').title())
                counts.append(len(findings))
            
            if not counts:
                logger.warning("No data for bar chart")
                return None
            
            # Ordenar por cantidad (descendente)
            sorted_data = sorted(zip(categories, counts), key=lambda x: x[1], reverse=True)
            categories, counts = zip(*sorted_data) if sorted_data else ([], [])
            
            # Crear gráfico
            fig = go.Figure(data=[
                go.Bar(
                    x=list(categories),
                    y=list(counts),
                    marker=dict(
                        color='#3498db',
                        line=dict(color='#2c3e50', width=1)
                    ),
                    text=list(counts),
                    textposition='outside'
                )
            ])
            
            fig.update_layout(
                title=dict(
                    text="Hallazgos por Categoría",
                    font=dict(size=18, color='#2c3e50')
                ),
                xaxis=dict(
                    title="Categoría",
                    tickangle=-45
                ),
                yaxis=dict(
                    title="Cantidad de Hallazgos"
                ),
                width=800,
                height=500,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(248,249,250,1)',
                showlegend=False
            )
            
            # Guardar como PNG
            if output_path:
                fig.write_image(str(output_path), format='png')
                logger.info(f"Bar chart saved to: {output_path}")
                return str(output_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating bar chart: {e}", exc_info=True)
            return None
    
    def create_risk_gauge(
        self,
        risk_score: float,
        output_path: Optional[Path] = None
    ) -> Optional[str]:
        """
        Crea un gráfico de indicador (gauge) para el risk score.
        
        Args:
            risk_score: Score de riesgo (0-10)
            output_path: Ruta donde guardar la imagen PNG (opcional)
            
        Returns:
            str: Path a la imagen PNG si output_path fue especificado,
                 None si falla
        """
        try:
            # Determinar color según el score
            if risk_score >= 8.0:
                color = '#e74c3c'  # Critical
                level_text = 'CRÍTICO'
            elif risk_score >= 6.0:
                color = '#e67e22'  # High
                level_text = 'ALTO'
            elif risk_score >= 4.0:
                color = '#f39c12'  # Medium
                level_text = 'MEDIO'
            elif risk_score >= 2.0:
                color = '#3498db'  # Low
                level_text = 'BAJO'
            else:
                color = '#95a5a6'  # Info
                level_text = 'MÍNIMO'
            
            # Crear gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=risk_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Risk Score<br><span style='font-size:0.6em'>{level_text}</span>"},
                delta={'reference': 5.0},  # Referencia media
                gauge={
                    'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': color},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 2], 'color': '#d4edda'},
                        {'range': [2, 4], 'color': '#cce5ff'},
                        {'range': [4, 6], 'color': '#fff3cd'},
                        {'range': [6, 8], 'color': '#f8d7da'},
                        {'range': [8, 10], 'color': '#f5c6cb'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 8.0
                    }
                }
            ))
            
            fig.update_layout(
                width=500,
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': "#2c3e50", 'family': "Arial"}
            )
            
            # Guardar como PNG
            if output_path:
                fig.write_image(str(output_path), format='png')
                logger.info(f"Risk gauge saved to: {output_path}")
                return str(output_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating risk gauge: {e}", exc_info=True)
            return None
    
    def generate_all_charts(
        self,
        severity_distribution: Dict[str, int],
        findings_by_category: Dict[str, List],
        risk_score: float,
        output_dir: Path
    ) -> Dict[str, str]:
        """
        Genera todos los gráficos y los guarda como PNG.
        
        Args:
            severity_distribution: Distribución de severidades
            findings_by_category: Findings por categoría
            risk_score: Score de riesgo
            output_dir: Directorio donde guardar las imágenes
            
        Returns:
            Dict con paths a las imágenes generadas
            Ej: {
                'severity_pie': '/path/to/severity_distribution.png',
                'category_bar': '/path/to/category_distribution.png',
                'risk_gauge': '/path/to/risk_gauge.png'
            }
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            charts = {}
            
            # Pie chart de severidades
            pie_path = output_dir / 'severity_distribution.png'
            pie_result = self.create_severity_pie_chart(severity_distribution, pie_path)
            if pie_result:
                charts['severity_pie'] = pie_result
            
            # Bar chart de categorías
            bar_path = output_dir / 'category_distribution.png'
            bar_result = self.create_category_bar_chart(findings_by_category, bar_path)
            if bar_result:
                charts['category_bar'] = bar_result
            
            # Gauge de risk score
            gauge_path = output_dir / 'risk_gauge.png'
            gauge_result = self.create_risk_gauge(risk_score, gauge_path)
            if gauge_result:
                charts['risk_gauge'] = gauge_result
            
            logger.info(f"Generated {len(charts)} charts in {output_dir}")
            return charts
            
        except Exception as e:
            logger.error(f"Error generating all charts: {e}", exc_info=True)
            return {}



