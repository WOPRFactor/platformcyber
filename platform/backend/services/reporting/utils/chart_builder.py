"""
Chart Builder
=============

Generador de gráficos para reportes usando Plotly.
Crea visualizaciones profesionales en formato PNG para incluir en PDFs.

Gráficos soportados:
- Pie Chart: Distribución de severidades (mejorado)
- Bar Chart: Hallazgos por categoría (mejorado)
- Gauge: Risk Score visual (mejorado)
- Heatmap: Severidad por categoría (nuevo)
- Treemap: Visualización jerárquica de categorías (nuevo)
- Stacked Bar: Severidad dentro de cada categoría (nuevo)
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
            
            # Crear gráfico mejorado con mejor diseño
            fig = go.Figure(data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    marker=dict(
                        colors=colors,
                        line=dict(color='#ffffff', width=2)
                    ),
                    textinfo='label+percent',
                    textposition='outside',
                    textfont=dict(size=12, color='#2c3e50'),
                    hovertemplate='<b>%{label}</b><br>Valor: %{value}<br>Porcentaje: %{percent}<extra></extra>',
                    hole=0.4  # Donut chart más elegante
                )
            ])
            
            fig.update_layout(
                title=dict(
                    text="Distribución de Hallazgos por Severidad",
                    font=dict(size=20, color='#2c3e50', family='Arial, sans-serif'),
                    x=0.5,
                    xanchor='center'
                ),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11, color='#555'),
                    itemclick="toggleothers"
                ),
                width=700,
                height=500,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=60, b=60, l=20, r=20)
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
            
            # Crear gráfico mejorado con gradientes y mejor diseño
            fig = go.Figure(data=[
                go.Bar(
                    x=list(categories),
                    y=list(counts),
                    marker=dict(
                        color=list(counts),
                        colorscale='Blues',
                        showscale=False,
                        line=dict(color='#2c3e50', width=1.5),
                        gradient=dict(
                            type='vertical',
                            color=['#e3f2fd', '#2196f3']
                        )
                    ),
                    text=list(counts),
                    textposition='outside',
                    textfont=dict(size=12, color='#2c3e50', family='Arial'),
                    hovertemplate='<b>%{x}</b><br>Hallazgos: %{y}<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title=dict(
                    text="Hallazgos por Categoría",
                    font=dict(size=20, color='#2c3e50', family='Arial, sans-serif'),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis=dict(
                    title=dict(text="Categoría", font=dict(size=13, color='#555')),
                    tickangle=-45,
                    tickfont=dict(size=11, color='#666'),
                    gridcolor='rgba(0,0,0,0.1)',
                    linecolor='#ddd'
                ),
                yaxis=dict(
                    title=dict(text="Cantidad de Hallazgos", font=dict(size=13, color='#555')),
                    tickfont=dict(size=11, color='#666'),
                    gridcolor='rgba(0,0,0,0.1)',
                    linecolor='#ddd'
                ),
                width=900,
                height=550,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(255,255,255,1)',
                showlegend=False,
                margin=dict(t=70, b=100, l=80, r=40)
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
                width=600,
                height=500,
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': "#2c3e50", 'family': "Arial, sans-serif", 'size': 12},
                margin=dict(t=60, b=60, l=40, r=40)
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
    
    def create_severity_heatmap(
        self,
        findings_by_category: Dict[str, List],
        output_path: Optional[Path] = None
    ) -> Optional[str]:
        """
        Crea un heatmap mostrando la distribución de severidades por categoría.
        
        Args:
            findings_by_category: Dict con findings organizados por categoría
            output_path: Ruta donde guardar la imagen PNG (opcional)
            
        Returns:
            str: Path a la imagen PNG si output_path fue especificado,
                 None si no hay datos o si falla
        """
        try:
            # Preparar datos para el heatmap
            categories = []
            severities = ['critical', 'high', 'medium', 'low', 'info']
            severity_labels = ['Critical', 'High', 'Medium', 'Low', 'Info']
            
            # Contar severidades por categoría
            data_matrix = []
            for category, findings in findings_by_category.items():
                categories.append(category.replace('_', ' ').title())
                row = []
                for severity in severities:
                    count = sum(1 for f in findings if f.severity == severity)
                    row.append(count)
                data_matrix.append(row)
            
            if not data_matrix or not categories:
                logger.warning("No data for heatmap")
                return None
            
            # Crear heatmap con paleta mejorada de alto contraste
            # Colores más oscuros desde el inicio para evitar mezclarse con el fondo
            fig = go.Figure(data=go.Heatmap(
                z=data_matrix,
                x=severity_labels,
                y=categories,
                colorscale=[
                    [0, '#2d5016'],      # Verde oscuro (bajo) - mejor contraste
                    [0.25, '#1e3a8a'],  # Azul oscuro
                    [0.5, '#b45309'],   # Amarillo oscuro/naranja
                    [0.75, '#991b1b'],  # Rojo oscuro
                    [1, '#7f1d1d']      # Rojo muy oscuro (crítico)
                ],
                text=[[str(val) if val > 0 else '' for val in row] for row in data_matrix],
                texttemplate='%{text}',
                textfont=dict(size=14, color='white', family='Arial, sans-serif', weight='bold'),
                colorbar=dict(
                    title=dict(text="Cantidad", font=dict(size=12, color='#2c3e50')),
                    tickfont=dict(size=10, color='#555'),
                    thickness=15,
                    len=0.5
                ),
                hovertemplate='<b>%{y}</b><br>Severidad: %{x}<br>Cantidad: %{z}<extra></extra>',
                showscale=True
            ))
            
            fig.update_layout(
                title=dict(
                    text="Distribución de Severidad por Categoría",
                    font=dict(size=20, color='#2c3e50', family='Arial, sans-serif'),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis=dict(
                    title=dict(text="Severidad", font=dict(size=13, color='#555')),
                    tickfont=dict(size=11, color='#666'),
                    gridcolor='rgba(0,0,0,0.1)',
                    linecolor='#ddd'
                ),
                yaxis=dict(
                    title=dict(text="Categoría", font=dict(size=13, color='#555')),
                    tickfont=dict(size=11, color='#666'),
                    gridcolor='rgba(0,0,0,0.1)',
                    linecolor='#ddd'
                ),
                width=800,
                height=max(400, len(categories) * 40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(248,249,250,1)',  # Fondo gris muy claro para mejor contraste
                margin=dict(t=70, b=60, l=150, r=80)
            )
            
            # Guardar como PNG
            if output_path:
                fig.write_image(str(output_path), format='png')
                logger.info(f"Heatmap saved to: {output_path}")
                return str(output_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating heatmap: {e}", exc_info=True)
            return None
    
    def create_category_treemap(
        self,
        findings_by_category: Dict[str, List],
        output_path: Optional[Path] = None
    ) -> Optional[str]:
        """
        Crea un treemap mostrando la distribución jerárquica de hallazgos por categoría.
        
        Args:
            findings_by_category: Dict con findings organizados por categoría
            output_path: Ruta donde guardar la imagen PNG (opcional)
            
        Returns:
            str: Path a la imagen PNG si output_path fue especificado,
                 None si no hay datos o si falla
        """
        try:
            # Preparar datos para treemap
            labels = []
            parents = []
            values = []
            colors_list = []
            
            # Colores para diferentes categorías
            category_colors = [
                '#3498db', '#e67e22', '#9b59b6', '#1abc9c', '#f39c12',
                '#e74c3c', '#34495e', '#16a085', '#27ae60', '#2980b9'
            ]
            
            total_findings = sum(len(findings) for findings in findings_by_category.values())
            if total_findings == 0:
                logger.warning("No data for treemap")
                return None
            
            # Agregar categorías
            for idx, (category, findings) in enumerate(findings_by_category.items()):
                category_label = category.replace('_', ' ').title()
                count = len(findings)
                if count > 0:
                    labels.append(f"{category_label}<br>({count})")
                    parents.append("")
                    values.append(count)
                    colors_list.append(category_colors[idx % len(category_colors)])
            
            # Crear treemap
            fig = go.Figure(go.Treemap(
                labels=labels,
                parents=parents,
                values=values,
                marker=dict(
                    colors=colors_list,
                    line=dict(color='white', width=2)
                ),
                textinfo='label+value',
                textfont=dict(size=14, color='white', family='Arial'),
                hovertemplate='<b>%{label}</b><br>Hallazgos: %{value}<br>Porcentaje: %{percentParent:.1%}<extra></extra>'
            ))
            
            fig.update_layout(
                title=dict(
                    text="Distribución de Hallazgos por Categoría (Treemap)",
                    font=dict(size=20, color='#2c3e50', family='Arial, sans-serif'),
                    x=0.5,
                    xanchor='center'
                ),
                width=900,
                height=600,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(255,255,255,1)',
                margin=dict(t=70, b=40, l=40, r=40)
            )
            
            # Guardar como PNG
            if output_path:
                fig.write_image(str(output_path), format='png')
                logger.info(f"Treemap saved to: {output_path}")
                return str(output_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating treemap: {e}", exc_info=True)
            return None
    
    def create_stacked_bar_chart(
        self,
        findings_by_category: Dict[str, List],
        output_path: Optional[Path] = None
    ) -> Optional[str]:
        """
        Crea un gráfico de barras apiladas mostrando severidad dentro de cada categoría.
        
        Args:
            findings_by_category: Dict con findings organizados por categoría
            output_path: Ruta donde guardar la imagen PNG (opcional)
            
        Returns:
            str: Path a la imagen PNG si output_path fue especificado,
                 None si no hay datos o si falla
        """
        try:
            # Preparar datos
            categories = []
            severities = ['critical', 'high', 'medium', 'low', 'info']
            severity_labels = ['Critical', 'High', 'Medium', 'Low', 'Info']
            
            # Contar severidades por categoría
            data_by_severity = {sev: [] for sev in severities}
            
            for category, findings in findings_by_category.items():
                categories.append(category.replace('_', ' ').title())
                for severity in severities:
                    count = sum(1 for f in findings if f.severity == severity)
                    data_by_severity[severity].append(count)
            
            if not categories:
                logger.warning("No data for stacked bar chart")
                return None
            
            # Crear gráfico apilado
            fig = go.Figure()
            
            for severity, label in zip(severities, severity_labels):
                fig.add_trace(go.Bar(
                    name=label,
                    x=categories,
                    y=data_by_severity[severity],
                    marker=dict(
                        color=self.SEVERITY_COLORS[severity],
                        line=dict(color='#ffffff', width=1)
                    ),
                    text=data_by_severity[severity],
                    textposition='inside',
                    textfont=dict(size=10, color='white'),
                    hovertemplate=f'<b>{label}</b><br>%{{x}}<br>Cantidad: %{{y}}<extra></extra>'
                ))
            
            fig.update_layout(
                title=dict(
                    text="Distribución de Severidad por Categoría (Barras Apiladas)",
                    font=dict(size=20, color='#2c3e50', family='Arial, sans-serif'),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis=dict(
                    title=dict(text="Categoría", font=dict(size=13, color='#555')),
                    tickangle=-45,
                    tickfont=dict(size=11, color='#666'),
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                yaxis=dict(
                    title=dict(text="Cantidad de Hallazgos", font=dict(size=13, color='#555')),
                    tickfont=dict(size=11, color='#666'),
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                barmode='stack',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.25,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11, color='#555')
                ),
                width=1000,
                height=600,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(255,255,255,1)',
                margin=dict(t=70, b=120, l=80, r=40)
            )
            
            # Guardar como PNG
            if output_path:
                fig.write_image(str(output_path), format='png')
                logger.info(f"Stacked bar chart saved to: {output_path}")
                return str(output_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating stacked bar chart: {e}", exc_info=True)
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
            
            # Heatmap de severidad por categoría
            heatmap_path = output_dir / 'severity_heatmap.png'
            heatmap_result = self.create_severity_heatmap(findings_by_category, heatmap_path)
            if heatmap_result:
                charts['severity_heatmap'] = heatmap_result
            
            # Treemap de categorías
            treemap_path = output_dir / 'category_treemap.png'
            treemap_result = self.create_category_treemap(findings_by_category, treemap_path)
            if treemap_result:
                charts['category_treemap'] = treemap_result
            
            # Stacked bar chart
            stacked_bar_path = output_dir / 'stacked_bar_chart.png'
            stacked_bar_result = self.create_stacked_bar_chart(findings_by_category, stacked_bar_path)
            if stacked_bar_result:
                charts['stacked_bar'] = stacked_bar_result
            
            logger.info(f"Generated {len(charts)} charts in {output_dir}")
            return charts
            
        except Exception as e:
            logger.error(f"Error generating all charts: {e}", exc_info=True)
            return {}



