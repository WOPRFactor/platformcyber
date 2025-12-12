# GUÍA DE IMPLEMENTACIÓN - MEJORAS MÓDULO DE REPORTERÍA

**Versión**: 1.0  
**Fecha**: 10 Diciembre 2025  
**Objetivo**: Completar funcionalidad del módulo de reportería V2

---

## 📋 ÍNDICE

1. [Contexto y Estado Actual](#contexto)
2. [Parte 1: Guardar Reportes en Base de Datos](#parte-1)
3. [Parte 2: Migrar a WeasyPrint para PDFs Profesionales](#parte-2)
4. [Parte 3: Agregar Gráficos con Plotly](#parte-3)
5. [Testing y Validación](#testing)
6. [Despliegue](#despliegue)

---

## 📊 CONTEXTO Y ESTADO ACTUAL {#contexto}

### Estado Actual del Sistema

**Lo que funciona ✅**:
- Parsers: 5 herramientas (Nmap, Nuclei, Nikto, Subfinder, Amass)
- Generación PDF: ReportLab básico
- Procesamiento asíncrono: Celery + Redis
- Frontend: React con progreso en tiempo real
- Tests: 62 tests unitarios, 90% coverage

**Lo que falta ❌**:
- Reportes NO se guardan en BD
- Diseño PDF básico (solo texto)
- Sin gráficos ni visualizaciones

### Arquitectura Actual

```
services/reporting/
├── config.py
├── core/
│   ├── file_scanner.py
│   ├── data_aggregator.py
│   └── risk_calculator.py
├── parsers/
│   ├── base_parser.py
│   ├── parser_manager.py
│   └── [5 parsers implementados]
├── generators/
│   └── pdf_generator_simple.py    ← Usa ReportLab
├── templates/
│   ├── base.html
│   └── technical/report.html
├── report_service_v2.py
└── reporting_tasks.py              ← Tarea Celery
```

---

## 🗄️ PARTE 1: GUARDAR REPORTES EN BASE DE DATOS {#parte-1}

### Objetivo

Persistir los reportes generados en la base de datos para:
- Mantener historial de reportes
- Permitir re-descarga
- Tracking de generaciones
- Auditoría

---

### 1.1 Verificar/Extender Modelo Report

**Ubicación**: `models/report.py`

El modelo debe tener estos campos mínimos:

```python
# models/report.py

from datetime import datetime
from extensions import db
import hashlib
from pathlib import Path

class Report(db.Model):
    """Modelo para reportes generados."""
    
    __tablename__ = 'reports'
    
    # IDs
    id = db.Column(db.Integer, primary_key=True)
    
    # Identificación del reporte
    title = db.Column(db.String(255), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # technical, executive, compliance
    format = db.Column(db.String(20), nullable=False)       # pdf, docx, html
    
    # Versionado
    version = db.Column(db.Integer, default=1, nullable=False)
    is_latest = db.Column(db.Boolean, default=True, nullable=False)
    
    # Archivo
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # bytes
    file_hash = db.Column(db.String(64))  # SHA-256
    
    # Metadata del contenido
    total_findings = db.Column(db.Integer, default=0)
    critical_count = db.Column(db.Integer, default=0)
    high_count = db.Column(db.Integer, default=0)
    medium_count = db.Column(db.Integer, default=0)
    low_count = db.Column(db.Integer, default=0)
    info_count = db.Column(db.Integer, default=0)
    risk_score = db.Column(db.Float)  # 0-10
    
    # Metadata de procesamiento
    files_processed = db.Column(db.Integer, default=0)
    tools_used = db.Column(db.JSON)  # ['nmap', 'nuclei', ...]
    generation_time_seconds = db.Column(db.Float)
    
    # Estado
    status = db.Column(db.String(20), default='pending', nullable=False)
    # Estados: pending, generating, completed, failed
    error_message = db.Column(db.Text)
    
    # Timestamps
    generated_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    workspace = db.relationship('Workspace', backref='reports')
    user = db.relationship('User', backref='reports')
    
    def calculate_file_hash(self):
        """Calcula SHA-256 hash del archivo."""
        file_path = Path(self.file_path)
        if not file_path.exists():
            return None
        
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verifica integridad del archivo."""
        if not self.file_hash:
            return False
        return self.calculate_file_hash() == self.file_hash
    
    def to_dict(self):
        """Serializa a diccionario."""
        return {
            'id': self.id,
            'title': self.title,
            'report_type': self.report_type,
            'format': self.format,
            'version': self.version,
            'is_latest': self.is_latest,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'total_findings': self.total_findings,
            'severity_counts': {
                'critical': self.critical_count,
                'high': self.high_count,
                'medium': self.medium_count,
                'low': self.low_count,
                'info': self.info_count
            },
            'risk_score': self.risk_score,
            'files_processed': self.files_processed,
            'tools_used': self.tools_used,
            'generation_time_seconds': self.generation_time_seconds,
            'status': self.status,
            'error_message': self.error_message,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'workspace_id': self.workspace_id,
            'created_by': self.created_by
        }
```

**Acción**: Verificar que el modelo actual tenga estos campos. Si faltan, agregarlos y crear migración.

---

### 1.2 Crear/Verificar Repository

**Ubicación**: `repositories/report_repository.py`

```python
# repositories/report_repository.py

from models.report import Report
from extensions import db
from typing import Optional, List
from datetime import datetime

class ReportRepository:
    """Repository para operaciones con reportes."""
    
    def create(self, **kwargs) -> Report:
        """
        Crea un nuevo reporte en la BD.
        
        Args:
            title: Título del reporte
            report_type: technical, executive, compliance
            format: pdf, docx, html
            workspace_id: ID del workspace
            created_by: ID del usuario
            file_path: Ruta al archivo generado
            file_size: Tamaño en bytes
            total_findings: Total de hallazgos
            critical_count, high_count, etc.: Contadores por severidad
            risk_score: Score de riesgo (0-10)
            files_processed: Cantidad de archivos parseados
            tools_used: Lista de herramientas detectadas
            generation_time_seconds: Tiempo de generación
            
        Returns:
            Report: Instancia creada y guardada
        """
        report = Report(**kwargs)
        
        # Calcular hash del archivo si existe
        if report.file_path:
            report.file_hash = report.calculate_file_hash()
        
        # Establecer estado y timestamp
        report.status = 'completed'
        report.generated_at = datetime.utcnow()
        
        db.session.add(report)
        db.session.commit()
        
        return report
    
    def find_by_id(self, report_id: int) -> Optional[Report]:
        """Busca un reporte por ID."""
        return Report.query.filter_by(id=report_id).first()
    
    def find_by_workspace(self, workspace_id: int, limit: int = 50) -> List[Report]:
        """
        Obtiene reportes de un workspace.
        
        Args:
            workspace_id: ID del workspace
            limit: Máximo de reportes a retornar
            
        Returns:
            Lista de reportes ordenados por fecha (más reciente primero)
        """
        return Report.query.filter_by(
            workspace_id=workspace_id
        ).order_by(
            Report.created_at.desc()
        ).limit(limit).all()
    
    def find_latest_by_type(
        self, 
        workspace_id: int, 
        report_type: str
    ) -> Optional[Report]:
        """Obtiene el reporte más reciente de un tipo específico."""
        return Report.query.filter_by(
            workspace_id=workspace_id,
            report_type=report_type,
            status='completed'
        ).order_by(
            Report.created_at.desc()
        ).first()
    
    def update_status(
        self, 
        report_id: int, 
        status: str, 
        error_message: str = None
    ) -> bool:
        """
        Actualiza el estado de un reporte.
        
        Args:
            report_id: ID del reporte
            status: Nuevo estado (pending, generating, completed, failed)
            error_message: Mensaje de error si falla
            
        Returns:
            True si se actualizó, False si no se encontró
        """
        report = self.find_by_id(report_id)
        if not report:
            return False
        
        report.status = status
        if error_message:
            report.error_message = error_message
        
        db.session.commit()
        return True
    
    def delete(self, report_id: int) -> bool:
        """
        Elimina un reporte de la BD y opcionalmente el archivo.
        
        Args:
            report_id: ID del reporte
            
        Returns:
            True si se eliminó, False si no se encontró
        """
        report = self.find_by_id(report_id)
        if not report:
            return False
        
        # Opcionalmente eliminar archivo físico
        from pathlib import Path
        file_path = Path(report.file_path)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                # Log pero no fallar
                import logging
                logging.error(f"Error deleting report file {file_path}: {e}")
        
        db.session.delete(report)
        db.session.commit()
        return True
```

**Acción**: Crear este archivo si no existe, o extender el existente con estos métodos.

---

### 1.3 Modificar Tarea Celery

**Ubicación**: `services/reporting/reporting_tasks.py`

**Cambios necesarios**:

1. Importar repository
2. Obtener/pasar `user_id`
3. Crear registro en BD después de generar PDF
4. Retornar `report_id` en lugar de solo `report_path`

**Pseudocódigo del cambio**:

```python
# reporting_tasks.py

from repositories.report_repository import ReportRepository
import time

@celery_app.task(bind=True, name='tasks.reporting.generate_report_v2')
def generate_report_v2(
    self, 
    workspace_id: int, 
    report_type: str = 'technical', 
    format_type: str = 'pdf',
    user_id: int = None  # ← NUEVO PARÁMETRO
):
    """Tarea Celery para generar reportes V2."""
    
    start_time = time.time()
    report_repo = ReportRepository()  # ← NUEVO
    
    try:
        with app.app_context():
            # ... código existente para generar PDF ...
            
            # Después de generar el PDF exitosamente:
            file_size = output_path.stat().st_size
            generation_time = time.time() - start_time
            
            # Determinar herramientas usadas
            tools_used = list(set([
                finding.raw_data.get('tool', 'unknown') 
                for finding in all_findings 
                if finding.raw_data
            ]))
            
            # ← NUEVO: Guardar en BD
            saved_report = report_repo.create(
                title=f"Reporte {report_type.title()} - {workspace.name}",
                report_type=report_type,
                format=format_type,
                workspace_id=workspace_id,
                created_by=user_id or 1,  # Default a admin si no hay user_id
                file_path=str(output_path),
                file_size=file_size,
                total_findings=len(all_findings),
                critical_count=severity_counts.get('critical', 0),
                high_count=severity_counts.get('high', 0),
                medium_count=severity_counts.get('medium', 0),
                low_count=severity_counts.get('low', 0),
                info_count=severity_counts.get('info', 0),
                risk_score=risk_metrics.get('risk_score', 0.0),
                files_processed=statistics.get('total_files', 0),
                tools_used=tools_used,
                generation_time_seconds=generation_time
            )
            
            # Actualizar progreso final
            self.update_state(
                state='SUCCESS',
                meta={
                    'status': 'completed',
                    'progress': 100,
                    'message': 'Reporte generado exitosamente',
                    'result': {
                        'report_id': saved_report.id,  # ← NUEVO
                        'workspace_id': workspace_id,
                        'report_path': str(output_path),
                        'file_size': file_size,
                        'statistics': statistics,
                        'risk_metrics': risk_metrics,
                        'metadata': {
                            'report_type': report_type,
                            'format': format_type,
                            'generation_time': generation_time,
                            'tools_used': tools_used
                        }
                    }
                }
            )
            
            return {
                'report_id': saved_report.id,  # ← NUEVO
                'report_path': str(output_path),
                'workspace_id': workspace_id,
                'file_size': file_size
            }
            
    except Exception as e:
        # Si falla, NO crear registro en BD (o crearlo con status='failed')
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'failed',
                'progress': 0,
                'message': f'Error: {str(e)}',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
        )
        raise
```

**Notas importantes**:
- `user_id` debe pasarse desde el endpoint que inicia la tarea
- Si no hay `user_id`, usar un default (ej: admin user_id=1)
- El `report_id` se retorna en el resultado para que el frontend lo use

---

### 1.4 Actualizar Endpoint de Generación

**Ubicación**: `services/reporting/routes.py` (o donde esté el endpoint)

**Cambio necesario**: Pasar `user_id` a la tarea Celery

```python
@reporting_bp.route('/generate-v2', methods=['POST'])
@jwt_required()
def generate_report_v2():
    """Genera un reporte V2 de forma asíncrona."""
    
    try:
        data = request.get_json()
        workspace_id = data.get('workspace_id')
        report_type = data.get('report_type', 'technical')
        format_type = data.get('format', 'pdf')
        
        # Obtener user_id del JWT
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()  # ← NUEVO
        
        # Validaciones...
        
        # Iniciar tarea Celery con user_id
        task = generate_report_v2_task.apply_async(
            args=[workspace_id, report_type, format_type, user_id],  # ← NUEVO
            task_id=str(uuid.uuid4())
        )
        
        return jsonify({
            'task_id': task.id,
            'status': 'pending',
            'message': 'Report generation started',
            'workspace_id': workspace_id,
            'report_type': report_type,
            'format': format_type
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

### 1.5 Crear Endpoint para Listar Reportes

**Nuevo endpoint**: `GET /api/v1/reporting/list/<workspace_id>`

```python
@reporting_bp.route('/list/<int:workspace_id>', methods=['GET'])
@jwt_required()
def list_reports(workspace_id):
    """
    Lista todos los reportes de un workspace.
    
    Query params opcionales:
    - limit: Máximo de reportes (default: 50)
    - report_type: Filtrar por tipo
    
    Returns:
    {
        "success": true,
        "reports": [
            {
                "id": 123,
                "title": "Reporte Técnico...",
                "report_type": "technical",
                "format": "pdf",
                "file_size": 2469,
                "risk_score": 7.8,
                "total_findings": 35,
                "severity_counts": {...},
                "created_at": "2025-12-10T10:30:00",
                "can_download": true
            },
            ...
        ]
    }
    """
    try:
        from repositories.report_repository import ReportRepository
        
        report_repo = ReportRepository()
        limit = request.args.get('limit', 50, type=int)
        report_type_filter = request.args.get('report_type')
        
        reports = report_repo.find_by_workspace(workspace_id, limit=limit)
        
        # Filtrar por tipo si se especifica
        if report_type_filter:
            reports = [r for r in reports if r.report_type == report_type_filter]
        
        # Verificar que los archivos existan
        from pathlib import Path
        reports_data = []
        for report in reports:
            data = report.to_dict()
            data['can_download'] = Path(report.file_path).exists()
            reports_data.append(data)
        
        return jsonify({
            'success': True,
            'reports': reports_data,
            'total': len(reports_data)
        }), 200
        
    except Exception as e:
        import logging
        logging.error(f"Error listing reports: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

### 1.6 Actualizar Endpoint de Descarga

**Modificar**: `POST /api/v1/reporting/download-by-path`

Para que también soporte descarga por `report_id`:

```python
@reporting_bp.route('/download', methods=['POST'])
@jwt_required()
def download_report():
    """
    Descarga un reporte por ID o path.
    
    Body:
    {
        "report_id": 123  // Opción 1: por ID
        // O
        "report_path": "/path/to/report.pdf"  // Opción 2: por path (legacy)
    }
    """
    try:
        data = request.get_json()
        report_id = data.get('report_id')
        report_path = data.get('report_path')
        
        from pathlib import Path
        
        # Opción 1: Buscar por ID (NUEVO)
        if report_id:
            from repositories.report_repository import ReportRepository
            report_repo = ReportRepository()
            report = report_repo.find_by_id(report_id)
            
            if not report:
                return jsonify({'error': 'Report not found'}), 404
            
            file_path = Path(report.file_path)
            filename = f"{report.title}.{report.format}"
        
        # Opción 2: Path directo (legacy, mantener por compatibilidad)
        elif report_path:
            file_path = Path(report_path)
            filename = file_path.name
        
        else:
            return jsonify({'error': 'report_id or report_path required'}), 400
        
        # Verificar existencia
        if not file_path.exists():
            return jsonify({'error': 'Report file not found'}), 404
        
        # Enviar archivo
        from flask import send_file
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        import logging
        logging.error(f"Error downloading report: {e}")
        return jsonify({'error': str(e)}), 500
```

---

### 1.7 Migración de Base de Datos

**Si usás Flask-Migrate (Alembic)**:

```bash
# Generar migración
flask db migrate -m "Add extended fields to Report model"

# Revisar archivo generado en migrations/versions/

# Aplicar migración
flask db upgrade
```

**Si NO usás migraciones**, ejecutar SQL manualmente:

```sql
-- Agregar campos nuevos al modelo Report (si faltan)
ALTER TABLE reports ADD COLUMN version INTEGER DEFAULT 1 NOT NULL;
ALTER TABLE reports ADD COLUMN is_latest BOOLEAN DEFAULT TRUE NOT NULL;
ALTER TABLE reports ADD COLUMN file_hash VARCHAR(64);
ALTER TABLE reports ADD COLUMN files_processed INTEGER DEFAULT 0;
ALTER TABLE reports ADD COLUMN tools_used JSON;
ALTER TABLE reports ADD COLUMN generation_time_seconds FLOAT;

-- Índices para búsquedas rápidas
CREATE INDEX idx_reports_workspace_type ON reports(workspace_id, report_type);
CREATE INDEX idx_reports_created_at ON reports(created_at DESC);
```

---

### 1.8 Actualizar Frontend (Opcional)

**Cambio en `ReportGeneratorV2.tsx`**:

Cuando el reporte se complete, usar `report_id` en lugar de `report_path`:

```typescript
// En el componente React
const handleDownload = async () => {
  try {
    const response = await fetch('/api/v1/reporting/download', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        report_id: taskResult.report_id  // ← Usar report_id
      })
    });
    
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `reporte_${Date.now()}.pdf`;
      a.click();
    }
  } catch (error) {
    console.error('Download error:', error);
  }
};
```

---

### 1.9 Checklist de Validación - Parte 1

- [ ] Modelo `Report` tiene todos los campos necesarios
- [ ] Migración de BD ejecutada exitosamente
- [ ] `ReportRepository` creado con todos los métodos
- [ ] Tarea Celery guarda reporte en BD después de generar PDF
- [ ] Tarea Celery retorna `report_id` en el resultado
- [ ] Endpoint de generación pasa `user_id` a la tarea
- [ ] Endpoint `/list/<workspace_id>` funciona y retorna reportes
- [ ] Endpoint `/download` soporta descargar por `report_id`
- [ ] Test manual: Generar reporte → Verificar que aparece en BD
- [ ] Test manual: Listar reportes → Ver reportes generados
- [ ] Test manual: Descargar por ID → Funciona correctamente

---

## 🎨 PARTE 2: MIGRAR A WEASYPRINT {#parte-2}

### Objetivo

Reemplazar ReportLab con WeasyPrint para generar PDFs con diseño profesional usando HTML/CSS.

**Ventajas**:
- ✅ Diseño mucho más bonito y profesional
- ✅ Usa HTML/CSS (más fácil de mantener que código Python)
- ✅ Soporta CSS moderno (Grid, Flexbox, etc.)
- ✅ Mejor manejo de estilos y colores
- ✅ Facilita agregar logos, imágenes, gráficos

---

### 2.1 Instalación de Dependencias

**Agregar a `requirements.txt`**:

```txt
# Generación de PDF
weasyprint==60.2
```

**Instalar**:

```bash
pip install weasyprint==60.2
```

**Dependencias del sistema** (si no están instaladas):

```bash
# Ubuntu/Debian
sudo apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info

# macOS
brew install pango gdk-pixbuf libffi
```

---

### 2.2 Crear Nuevo Generador con WeasyPrint

**Ubicación**: `services/reporting/generators/pdf_generator_weasy.py`

```python
# services/reporting/generators/pdf_generator_weasy.py

"""
Generador de PDFs profesionales usando WeasyPrint.
Convierte templates HTML/CSS a PDF.
"""

from pathlib import Path
from typing import Dict, Any, List
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
import logging

logger = logging.getLogger(__name__)

class WeasyPrintPDFGenerator:
    """Generador de PDFs usando WeasyPrint + Jinja2."""
    
    def __init__(self):
        # Configurar Jinja2 para templates
        template_dir = Path(__file__).parent.parent / 'templates'
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
    
    def generate_technical_report(
        self,
        output_path: Path,
        workspace_name: str,
        findings: List[Any],
        statistics: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Path:
        """
        Genera un reporte técnico en PDF.
        
        Args:
            output_path: Ruta donde guardar el PDF
            workspace_name: Nombre del workspace
            findings: Lista de findings consolidados
            statistics: Estadísticas del escaneo
            risk_metrics: Métricas de riesgo
            metadata: Metadata adicional
            
        Returns:
            Path al archivo PDF generado
        """
        try:
            logger.info(f"Generating technical report with WeasyPrint: {output_path}")
            
            # Preparar datos para el template
            template_data = self._prepare_template_data(
                workspace_name=workspace_name,
                findings=findings,
                statistics=statistics,
                risk_metrics=risk_metrics,
                metadata=metadata
            )
            
            # Renderizar template HTML
            template = self.jinja_env.get_template('technical/report_weasy.html')
            html_content = template.render(**template_data)
            
            # Convertir HTML a PDF
            HTML(string=html_content).write_pdf(
                target=str(output_path),
                stylesheets=[self._get_pdf_stylesheet()]
            )
            
            logger.info(f"PDF generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF with WeasyPrint: {e}")
            raise
    
    def _prepare_template_data(
        self,
        workspace_name: str,
        findings: List[Any],
        statistics: Dict[str, Any],
        risk_metrics: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepara datos estructurados para el template."""
        
        from datetime import datetime
        
        # Organizar findings por categoría
        findings_by_category = {}
        for finding in findings:
            category = finding.category
            if category not in findings_by_category:
                findings_by_category[category] = []
            findings_by_category[category].append(finding)
        
        # Ordenar por severidad dentro de cada categoría
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        for category in findings_by_category:
            findings_by_category[category].sort(
                key=lambda f: (severity_order.get(f.severity, 999), f.title)
            )
        
        # Obtener top vulnerabilidades críticas/altas
        critical_and_high = [
            f for f in findings 
            if f.severity in ['critical', 'high']
        ][:10]  # Top 10
        
        return {
            'workspace_name': workspace_name,
            'report_date': datetime.now().strftime('%d de %B, %Y'),
            'report_time': datetime.now().strftime('%H:%M'),
            
            # Findings
            'findings': findings,
            'findings_by_category': findings_by_category,
            'critical_findings': critical_and_high,
            
            # Estadísticas
            'total_findings': statistics.get('total_findings', 0),
            'total_files': statistics.get('total_files', 0),
            'unique_targets': statistics.get('unique_targets', 0),
            'files_by_category': statistics.get('files_by_category', {}),
            
            # Risk metrics
            'risk_score': risk_metrics.get('risk_score', 0.0),
            'risk_level': risk_metrics.get('risk_level', 'unknown'),
            'severity_distribution': risk_metrics.get('severity_distribution', {}),
            
            # Metadata
            'tools_used': metadata.get('tools_used', []),
            'generation_time': metadata.get('generation_time', 0),
        }
    
    def _get_pdf_stylesheet(self) -> CSS:
        """Retorna stylesheet CSS para el PDF."""
        
        css_content = """
        @page {
            size: A4;
            margin: 2cm;
            
            @top-center {
                content: "Reporte Técnico de Seguridad";
                font-family: Arial, sans-serif;
                font-size: 10pt;
                color: #666;
            }
            
            @bottom-right {
                content: "Página " counter(page) " de " counter(pages);
                font-family: Arial, sans-serif;
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: Arial, Helvetica, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 24pt;
            margin-bottom: 10pt;
            page-break-after: avoid;
        }
        
        h2 {
            color: #34495e;
            font-size: 18pt;
            margin-top: 20pt;
            margin-bottom: 10pt;
            page-break-after: avoid;
        }
        
        h3 {
            color: #555;
            font-size: 14pt;
            margin-top: 15pt;
            margin-bottom: 8pt;
            page-break-after: avoid;
        }
        
        /* Evitar que elementos se corten entre páginas */
        .finding-card, .stat-box, .section-box {
            page-break-inside: avoid;
        }
        
        /* Colores de severidad */
        .severity-critical {
            color: #ffffff;
            background-color: #e74c3c;
            padding: 4pt 10pt;
            border-radius: 12pt;
            font-weight: bold;
            font-size: 10pt;
        }
        
        .severity-high {
            color: #ffffff;
            background-color: #e67e22;
            padding: 4pt 10pt;
            border-radius: 12pt;
            font-weight: bold;
            font-size: 10pt;
        }
        
        .severity-medium {
            color: #ffffff;
            background-color: #f39c12;
            padding: 4pt 10pt;
            border-radius: 12pt;
            font-weight: bold;
            font-size: 10pt;
        }
        
        .severity-low {
            color: #ffffff;
            background-color: #3498db;
            padding: 4pt 10pt;
            border-radius: 12pt;
            font-weight: bold;
            font-size: 10pt;
        }
        
        .severity-info {
            color: #ffffff;
            background-color: #95a5a6;
            padding: 4pt 10pt;
            border-radius: 12pt;
            font-weight: bold;
            font-size: 10pt;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10pt 0;
        }
        
        table th {
            background-color: #34495e;
            color: white;
            padding: 8pt;
            text-align: left;
            font-weight: bold;
        }
        
        table td {
            padding: 8pt;
            border-bottom: 1px solid #ddd;
        }
        
        table tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        code {
            background-color: #f4f4f4;
            padding: 2pt 6pt;
            border-radius: 3pt;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }
        
        pre {
            background-color: #f4f4f4;
            padding: 10pt;
            border-radius: 4pt;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            line-height: 1.4;
        }
        """
        
        return CSS(string=css_content)
```

---

### 2.3 Crear Template HTML para Reporte Técnico

**Ubicación**: `services/reporting/templates/technical/report_weasy.html`

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte Técnico - {{ workspace_name }}</title>
    <style>
        /* Estilos inline para WeasyPrint */
        
        /* Portada */
        .cover-page {
            text-align: center;
            padding-top: 200pt;
        }
        
        .cover-title {
            font-size: 36pt;
            color: #2c3e50;
            font-weight: bold;
            margin-bottom: 20pt;
        }
        
        .cover-subtitle {
            font-size: 20pt;
            color: #7f8c8d;
            margin-bottom: 40pt;
        }
        
        .cover-info {
            font-size: 14pt;
            color: #555;
            line-height: 2;
        }
        
        /* Risk Score Box */
        .risk-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20pt;
            border-radius: 10pt;
            text-align: center;
            margin: 20pt 0;
            page-break-inside: avoid;
        }
        
        .risk-score {
            font-size: 48pt;
            font-weight: bold;
            margin: 10pt 0;
        }
        
        .risk-level {
            font-size: 18pt;
            text-transform: uppercase;
            letter-spacing: 2pt;
        }
        
        /* Stats Grid */
        .stats-grid {
            display: table;
            width: 100%;
            margin: 20pt 0;
        }
        
        .stat-row {
            display: table-row;
        }
        
        .stat-cell {
            display: table-cell;
            width: 25%;
            padding: 15pt;
            text-align: center;
            border: 1pt solid #e0e0e0;
        }
        
        .stat-number {
            font-size: 36pt;
            font-weight: bold;
            margin: 10pt 0;
        }
        
        .stat-number.critical { color: #e74c3c; }
        .stat-number.high { color: #e67e22; }
        .stat-number.medium { color: #f39c12; }
        .stat-number.info { color: #3498db; }
        
        .stat-label {
            font-size: 10pt;
            color: #666;
            text-transform: uppercase;
        }
        
        /* Finding Card */
        .finding-card {
            border-left: 5pt solid #e74c3c;
            background: #f8f9fa;
            padding: 15pt;
            margin: 15pt 0;
            border-radius: 5pt;
            page-break-inside: avoid;
        }
        
        .finding-card.high { border-left-color: #e67e22; }
        .finding-card.medium { border-left-color: #f39c12; }
        .finding-card.low { border-left-color: #3498db; }
        .finding-card.info { border-left-color: #95a5a6; }
        
        .finding-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10pt;
        }
        
        .finding-title {
            font-size: 14pt;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .finding-description {
            color: #555;
            margin: 8pt 0;
            line-height: 1.6;
        }
        
        .finding-target {
            background: #fff;
            padding: 8pt;
            border-radius: 4pt;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            color: #333;
            margin: 8pt 0;
        }
        
        .finding-evidence {
            background: #fffbf0;
            border-left: 3pt solid #f39c12;
            padding: 10pt;
            margin: 10pt 0;
            font-size: 10pt;
        }
        
        .finding-remediation {
            background: #f0fff4;
            border-left: 3pt solid #28a745;
            padding: 10pt;
            margin: 10pt 0;
        }
        
        /* Section Box */
        .section-box {
            background: #f8f9fa;
            border: 1pt solid #e0e0e0;
            padding: 15pt;
            margin: 15pt 0;
            border-radius: 5pt;
            page-break-inside: avoid;
        }
    </style>
</head>
<body>
    <!-- PORTADA -->
    <div class="cover-page">
        <div class="cover-title">Reporte Técnico de Seguridad</div>
        <div class="cover-subtitle">Evaluación de Vulnerabilidades</div>
        <div class="cover-info">
            <strong>Workspace:</strong> {{ workspace_name }}<br>
            <strong>Fecha:</strong> {{ report_date }}<br>
            <strong>Hora:</strong> {{ report_time }}
        </div>
    </div>
    
    <!-- Nueva página -->
    <div style="page-break-before: always;"></div>
    
    <!-- RESUMEN EJECUTIVO -->
    <h1>Resumen Ejecutivo</h1>
    
    <div class="risk-box">
        <div>Puntuación de Riesgo Global</div>
        <div class="risk-score">{{ "%.1f"|format(risk_score) }}/10</div>
        <div class="risk-level">{{ risk_level.upper() }}</div>
    </div>
    
    <div class="section-box">
        <p>
            Se realizó una evaluación de seguridad integral de <strong>{{ workspace_name }}</strong>. 
            El análisis identificó <strong>{{ total_findings }} hallazgos</strong> de severidad variable.
        </p>
        {% if severity_distribution.critical > 0 %}
        <p style="margin-top: 10pt; color: #e74c3c;">
            ⚠️ Se encontraron <strong>{{ severity_distribution.critical }} vulnerabilidades críticas</strong> 
            que requieren atención inmediata.
        </p>
        {% endif %}
    </div>
    
    <h2>Estadísticas del Escaneo</h2>
    
    <div class="stats-grid">
        <div class="stat-row">
            <div class="stat-cell">
                <div class="stat-label">Críticas</div>
                <div class="stat-number critical">{{ severity_distribution.critical or 0 }}</div>
            </div>
            <div class="stat-cell">
                <div class="stat-label">Altas</div>
                <div class="stat-number high">{{ severity_distribution.high or 0 }}</div>
            </div>
            <div class="stat-cell">
                <div class="stat-label">Medias</div>
                <div class="stat-number medium">{{ severity_distribution.medium or 0 }}</div>
            </div>
            <div class="stat-cell">
                <div class="stat-label">Bajas/Info</div>
                <div class="stat-number info">{{ (severity_distribution.low or 0) + (severity_distribution.info or 0) }}</div>
            </div>
        </div>
    </div>
    
    <table>
        <tr>
            <th>Métrica</th>
            <th>Valor</th>
        </tr>
        <tr>
            <td>Total de Hallazgos</td>
            <td><strong>{{ total_findings }}</strong></td>
        </tr>
        <tr>
            <td>Archivos Procesados</td>
            <td>{{ total_files }}</td>
        </tr>
        <tr>
            <td>Targets Únicos</td>
            <td>{{ unique_targets }}</td>
        </tr>
        <tr>
            <td>Herramientas Utilizadas</td>
            <td>{{ tools_used|join(', ') }}</td>
        </tr>
        <tr>
            <td>Tiempo de Generación</td>
            <td>{{ "%.2f"|format(generation_time) }} segundos</td>
        </tr>
    </table>
    
    <!-- Nueva página -->
    <div style="page-break-before: always;"></div>
    
    <!-- HALLAZGOS CRÍTICOS -->
    {% if critical_findings %}
    <h1>Hallazgos Críticos y Altos</h1>
    
    {% for finding in critical_findings %}
    <div class="finding-card {{ finding.severity }}">
        <div class="finding-header">
            <div class="finding-title">{{ finding.title }}</div>
            <span class="severity-{{ finding.severity }}">{{ finding.severity.upper() }}</span>
        </div>
        
        <div class="finding-target">
            <strong>Target:</strong> {{ finding.affected_target }}
        </div>
        
        {% if finding.description %}
        <div class="finding-description">
            {{ finding.description }}
        </div>
        {% endif %}
        
        {% if finding.evidence %}
        <div class="finding-evidence">
            <strong>Evidencia:</strong><br>
            {{ finding.evidence[:200] }}{% if finding.evidence|length > 200 %}...{% endif %}
        </div>
        {% endif %}
        
        {% if finding.remediation %}
        <div class="finding-remediation">
            <strong>Remediación:</strong><br>
            {{ finding.remediation }}
        </div>
        {% endif %}
        
        {% if finding.cve_id %}
        <div style="margin-top: 8pt; font-size: 10pt; color: #666;">
            <strong>CVE:</strong> {{ finding.cve_id }}
        </div>
        {% endif %}
        
        {% if finding.references %}
        <div style="margin-top: 8pt; font-size: 10pt; color: #666;">
            <strong>Referencias:</strong>
            {% for ref in finding.references[:3] %}
                <br>• {{ ref }}
            {% endfor %}
        </div>
        {% endif %}
    </div>
    {% endfor %}
    {% endif %}
    
    <!-- Nueva página -->
    <div style="page-break-before: always;"></div>
    
    <!-- HALLAZGOS POR CATEGORÍA -->
    <h1>Hallazgos Detallados por Categoría</h1>
    
    {% for category, category_findings in findings_by_category.items() %}
    <h2>{{ category|replace('_', ' ')|title }}</h2>
    
    <p>Total de hallazgos en esta categoría: <strong>{{ category_findings|length }}</strong></p>
    
    {% for finding in category_findings[:20] %}  {# Limitar a 20 por categoría #}
    <div class="finding-card {{ finding.severity }}">
        <div class="finding-header">
            <div class="finding-title">{{ finding.title }}</div>
            <span class="severity-{{ finding.severity }}">{{ finding.severity.upper() }}</span>
        </div>
        
        <div class="finding-target">
            <strong>Target:</strong> {{ finding.affected_target }}
        </div>
        
        {% if finding.description %}
        <div class="finding-description">
            {{ finding.description }}
        </div>
        {% endif %}
    </div>
    {% endfor %}
    
    {% if category_findings|length > 20 %}
    <p style="color: #666; font-style: italic;">
        ... y {{ category_findings|length - 20 }} hallazgos más en esta categoría.
    </p>
    {% endif %}
    
    {% endfor %}
    
    <!-- CONCLUSIÓN -->
    <div style="page-break-before: always;"></div>
    
    <h1>Conclusión</h1>
    
    <div class="section-box">
        <p>
            Este reporte técnico documenta los hallazgos de seguridad identificados durante 
            la evaluación de <strong>{{ workspace_name }}</strong>.
        </p>
        
        {% if severity_distribution.critical > 0 or severity_distribution.high > 0 %}
        <p style="margin-top: 10pt; color: #e74c3c;">
            Se recomienda priorizar la remediación de las vulnerabilidades críticas y altas 
            documentadas en este reporte.
        </p>
        {% endif %}
        
        <p style="margin-top: 10pt;">
            Para más información o asistencia en la remediación, por favor contacte al equipo 
            de seguridad.
        </p>
    </div>
    
    <div style="margin-top: 30pt; padding: 15pt; background: #e8f4f8; border-radius: 5pt;">
        <p style="font-size: 10pt; color: #666; text-align: center;">
            Reporte generado automáticamente el {{ report_date }} a las {{ report_time }}<br>
            Workspace: {{ workspace_name }} | Total de hallazgos: {{ total_findings }}
        </p>
    </div>
</body>
</html>
```

---

### 2.4 Modificar Tarea Celery para Usar WeasyPrint

**En `reporting_tasks.py`**, cambiar el generador:

```python
# reporting_tasks.py

# ANTES (ReportLab):
# from services.reporting.generators.pdf_generator_simple import SimplePDFGenerator
# generator = SimplePDFGenerator()

# DESPUÉS (WeasyPrint):
from services.reporting.generators.pdf_generator_weasy import WeasyPrintPDFGenerator

generator = WeasyPrintPDFGenerator()

# Llamar al generador
output_path = generator.generate_technical_report(
    output_path=output_path,
    workspace_name=workspace.name,
    findings=all_findings,
    statistics=statistics,
    risk_metrics=risk_metrics,
    metadata=metadata
)
```

---

### 2.5 Prueba de Generación

**Test manual**:

```python
# test_weasyprint.py (crear temporalmente para probar)

from services.reporting.generators.pdf_generator_weasy import WeasyPrintPDFGenerator
from services.reporting.parsers.base_parser import ParsedFinding
from pathlib import Path

# Datos de prueba
findings = [
    ParsedFinding(
        title="SQL Injection en Login",
        severity="critical",
        description="Vulnerabilidad de inyección SQL en el formulario de login",
        category="vulnerability",
        affected_target="https://example.com/login",
        evidence="' OR '1'='1' -- bypasses authentication",
        remediation="Usar prepared statements o parametrized queries"
    ),
    ParsedFinding(
        title="Puerto SSH Abierto",
        severity="low",
        description="Puerto 22 expuesto públicamente",
        category="port_scan",
        affected_target="192.168.1.100:22"
    )
]

statistics = {
    'total_findings': 2,
    'total_files': 5,
    'unique_targets': 2
}

risk_metrics = {
    'risk_score': 7.8,
    'risk_level': 'high',
    'severity_distribution': {
        'critical': 1,
        'high': 0,
        'medium': 0,
        'low': 1,
        'info': 0
    }
}

metadata = {
    'tools_used': ['nmap', 'nuclei'],
    'generation_time': 2.5
}

# Generar PDF de prueba
generator = WeasyPrintPDFGenerator()
output = generator.generate_technical_report(
    output_path=Path('/tmp/test_report.pdf'),
    workspace_name="Test Workspace",
    findings=findings,
    statistics=statistics,
    risk_metrics=risk_metrics,
    metadata=metadata
)

print(f"PDF generado en: {output}")
```

---

### 2.6 Checklist de Validación - Parte 2

- [ ] WeasyPrint instalado correctamente
- [ ] Dependencias del sistema instaladas (Pango, Cairo)
- [ ] `WeasyPrintPDFGenerator` creado y funcional
- [ ] Template HTML `report_weasy.html` creado
- [ ] Test manual genera PDF correctamente
- [ ] PDF tiene diseño profesional (colores, estilos)
- [ ] Severidades se muestran con colores correctos
- [ ] Portada se ve bien
- [ ] Saltos de página funcionan correctamente
- [ ] Tarea Celery modificada para usar WeasyPrint
- [ ] Test end-to-end: Generar reporte desde frontend → PDF profesional

---

## 📊 PARTE 3: AGREGAR GRÁFICOS CON PLOTLY {#parte-3}

### Objetivo

Agregar visualizaciones gráficas al reporte para hacerlo más profesional y visual.

**Gráficos a implementar**:
1. ✅ Pie Chart: Distribución de severidades
2. ✅ Bar Chart: Hallazgos por categoría
3. ✅ Gauge: Risk Score visual

---

### 3.1 Instalación de Dependencias

**Agregar a `requirements.txt`**:

```txt
# Gráficos y visualizaciones
plotly==5.18.0
kaleido==0.2.1
```

**Instalar**:

```bash
pip install plotly==5.18.0 kaleido==0.2.1
```

---

### 3.2 Crear Módulo de Gráficos

**Ubicación**: `services/reporting/utils/chart_builder.py`

```python
# services/reporting/utils/chart_builder.py

"""
Generador de gráficos para reportes usando Plotly.
"""

import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class ChartBuilder:
    """Construye gráficos para reportes."""
    
    # Colores por severidad
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
        output_path: Path = None
    ) -> str:
        """
        Crea un gráfico de torta (pie chart) de distribución de severidades.
        
        Args:
            severity_distribution: Dict con contadores por severidad
            output_path: Ruta donde guardar la imagen PNG (opcional)
            
        Returns:
            str: HTML del gráfico o path a la imagen
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
            
            # Si se especifica output_path, guardar como PNG
            if output_path:
                fig.write_image(str(output_path), format='png')
                return str(output_path)
            
            # Sino, retornar HTML
            return fig.to_html(include_plotlyjs='cdn', div_id='severity_pie_chart')
            
        except Exception as e:
            logger.error(f"Error creating pie chart: {e}")
            return None
    
    def create_category_bar_chart(
        self,
        findings_by_category: Dict[str, List],
        output_path: Path = None
    ) -> str:
        """
        Crea un gráfico de barras de hallazgos por categoría.
        
        Args:
            findings_by_category: Dict con findings organizados por categoría
            output_path: Ruta donde guardar la imagen PNG (opcional)
            
        Returns:
            str: HTML del gráfico o path a la imagen
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
            
            # Guardar o retornar HTML
            if output_path:
                fig.write_image(str(output_path), format='png')
                return str(output_path)
            
            return fig.to_html(include_plotlyjs='cdn', div_id='category_bar_chart')
            
        except Exception as e:
            logger.error(f"Error creating bar chart: {e}")
            return None
    
    def create_risk_gauge(
        self,
        risk_score: float,
        output_path: Path = None
    ) -> str:
        """
        Crea un gráfico de indicador (gauge) para el risk score.
        
        Args:
            risk_score: Score de riesgo (0-10)
            output_path: Ruta donde guardar la imagen PNG (opcional)
            
        Returns:
            str: HTML del gráfico o path a la imagen
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
            
            # Guardar o retornar HTML
            if output_path:
                fig.write_image(str(output_path), format='png')
                return str(output_path)
            
            return fig.to_html(include_plotlyjs='cdn', div_id='risk_gauge')
            
        except Exception as e:
            logger.error(f"Error creating risk gauge: {e}")
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
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        charts = {}
        
        # Pie chart de severidades
        pie_path = output_dir / 'severity_distribution.png'
        if self.create_severity_pie_chart(severity_distribution, pie_path):
            charts['severity_pie'] = str(pie_path)
        
        # Bar chart de categorías
        bar_path = output_dir / 'category_distribution.png'
        if self.create_category_bar_chart(findings_by_category, bar_path):
            charts['category_bar'] = str(bar_path)
        
        # Gauge de risk score
        gauge_path = output_dir / 'risk_gauge.png'
        if self.create_risk_gauge(risk_score, gauge_path):
            charts['risk_gauge'] = str(gauge_path)
        
        return charts
```

---

### 3.3 Integrar Gráficos en el Generador de PDF

**Modificar `pdf_generator_weasy.py`**:

```python
# En pdf_generator_weasy.py

from .utils.chart_builder import ChartBuilder

class WeasyPrintPDFGenerator:
    
    def __init__(self):
        # ... código existente ...
        self.chart_builder = ChartBuilder()  # ← NUEVO
    
    def generate_technical_report(self, ...):
        try:
            # ... código existente de preparación ...
            
            # ← NUEVO: Generar gráficos
            charts_dir = output_path.parent / 'charts'
            charts = self.chart_builder.generate_all_charts(
                severity_distribution=risk_metrics['severity_distribution'],
                findings_by_category=self._organize_by_category(findings),
                risk_score=risk_metrics['risk_score'],
                output_dir=charts_dir
            )
            
            # Agregar paths de gráficos a template_data
            template_data['charts'] = charts
            
            # ... resto del código ...
```

**Modificar template HTML** para incluir gráficos:

```html
<!-- En report_weasy.html, agregar después del resumen ejecutivo -->

{% if charts %}
<h2>Visualizaciones</h2>

<div style="text-align: center; margin: 20pt 0;">
    {% if charts.risk_gauge %}
    <img src="{{ charts.risk_gauge }}" alt="Risk Gauge" style="max-width: 500px;">
    {% endif %}
</div>

<div style="display: table; width: 100%; margin: 20pt 0;">
    {% if charts.severity_pie %}
    <div style="display: table-cell; width: 50%; padding: 10pt;">
        <img src="{{ charts.severity_pie }}" alt="Severity Distribution" style="width: 100%;">
    </div>
    {% endif %}
    
    {% if charts.category_bar %}
    <div style="display: table-cell; width: 50%; padding: 10pt;">
        <img src="{{ charts.category_bar }}" alt="Category Distribution" style="width: 100%;">
    </div>
    {% endif %}
</div>
{% endif %}
```

---

### 3.4 Checklist de Validación - Parte 3

- [ ] Plotly y Kaleido instalados correctamente
- [ ] `ChartBuilder` creado y funcional
- [ ] Test de generación de pie chart funciona
- [ ] Test de generación de bar chart funciona
- [ ] Test de generación de gauge funciona
- [ ] Gráficos se generan como PNG correctamente
- [ ] PDFGenerator integra gráficos
- [ ] Template HTML muestra gráficos
- [ ] Test end-to-end: PDF con gráficos se ve bien
- [ ] Gráficos tienen calidad adecuada (no pixelados)

---

## 🧪 TESTING Y VALIDACIÓN {#testing}

### Tests Unitarios

**Crear**: `tests/unit/test_report_repository.py`

```python
import pytest
from repositories.report_repository import ReportRepository
from models.report import Report

def test_create_report(db_session):
    """Test crear un reporte."""
    repo = ReportRepository()
    
    report = repo.create(
        title="Test Report",
        report_type="technical",
        format="pdf",
        workspace_id=1,
        created_by=1,
        file_path="/tmp/test.pdf",
        file_size=1024,
        total_findings=10,
        critical_count=2,
        risk_score=7.5
    )
    
    assert report.id is not None
    assert report.title == "Test Report"
    assert report.status == "completed"

def test_find_by_workspace(db_session):
    """Test buscar reportes por workspace."""
    repo = ReportRepository()
    
    # Crear reportes de prueba
    repo.create(title="Report 1", workspace_id=1, ...)
    repo.create(title="Report 2", workspace_id=1, ...)
    repo.create(title="Report 3", workspace_id=2, ...)
    
    # Buscar workspace 1
    reports = repo.find_by_workspace(1)
    assert len(reports) == 2
```

**Crear**: `tests/unit/test_weasyprint_generator.py`

```python
import pytest
from pathlib import Path
from services.reporting.generators.pdf_generator_weasy import WeasyPrintPDFGenerator
from services.reporting.parsers.base_parser import ParsedFinding

def test_generate_pdf():
    """Test generar PDF con WeasyPrint."""
    generator = WeasyPrintPDFGenerator()
    
    findings = [
        ParsedFinding(
            title="Test Finding",
            severity="high",
            description="Test description",
            category="test",
            affected_target="test.com"
        )
    ]
    
    output_path = Path("/tmp/test_report.pdf")
    
    result = generator.generate_technical_report(
        output_path=output_path,
        workspace_name="Test",
        findings=findings,
        statistics={'total_findings': 1},
        risk_metrics={'risk_score': 5.0, 'severity_distribution': {'high': 1}},
        metadata={'tools_used': ['test']}
    )
    
    assert result.exists()
    assert result.stat().st_size > 0
```

**Crear**: `tests/unit/test_chart_builder.py`

```python
import pytest
from pathlib import Path
from services.reporting.utils.chart_builder import ChartBuilder

def test_create_pie_chart():
    """Test crear gráfico de torta."""
    builder = ChartBuilder()
    
    severity_dist = {
        'critical': 5,
        'high': 12,
        'medium': 18
    }
    
    output_path = Path("/tmp/test_pie.png")
    result = builder.create_severity_pie_chart(severity_dist, output_path)
    
    assert output_path.exists()
    assert output_path.stat().st_size > 0
```

---

### Tests de Integración

**Crear**: `tests/integration/test_full_report_generation.py`

```python
import pytest
from services.reporting.report_service_v2 import ReportServiceV2
from services.reporting.reporting_tasks import generate_report_v2

def test_full_report_generation_with_db(app, db_session):
    """Test generación completa de reporte con guardado en BD."""
    
    with app.app_context():
        # Ejecutar tarea
        result = generate_report_v2(
            workspace_id=10,
            report_type='technical',
            format_type='pdf',
            user_id=1
        )
        
        # Verificar resultado
        assert 'report_id' in result
        assert result['report_id'] is not None
        
        # Verificar en BD
        from repositories.report_repository import ReportRepository
        repo = ReportRepository()
        report = repo.find_by_id(result['report_id'])
        
        assert report is not None
        assert report.status == 'completed'
        assert report.file_path.endswith('.pdf')
```

---

### Validación Manual

**Checklist de pruebas manuales**:

1. **Generación básica**:
   - [ ] Crear reporte desde frontend
   - [ ] Ver progreso en tiempo real
   - [ ] Descargar PDF generado
   - [ ] PDF se abre correctamente

2. **Diseño del PDF**:
   - [ ] Portada se ve profesional
   - [ ] Colores de severidad correctos
   - [ ] Gráficos se ven bien
   - [ ] No hay elementos cortados entre páginas
   - [ ] Tablas formateadas correctamente

3. **Base de datos**:
   - [ ] Reporte aparece en BD después de generar
   - [ ] Campos poblados correctamente
   - [ ] Hash del archivo calculado
   - [ ] Endpoint `/list/<workspace_id>` retorna el reporte
   - [ ] Descarga por `report_id` funciona

4. **Gráficos**:
   - [ ] Pie chart muestra distribución correcta
   - [ ] Bar chart muestra categorías correctas
   - [ ] Gauge muestra risk score correcto
   - [ ] Imágenes no pixeladas

---

## 🚀 DESPLIEGUE {#despliegue}

### Pasos de Despliegue

1. **Instalar dependencias nuevas**:
```bash
pip install -r requirements.txt
```

2. **Instalar dependencias del sistema** (si es necesario):
```bash
sudo apt-get update
sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0
```

3. **Ejecutar migraciones de BD**:
```bash
flask db upgrade
# O ejecutar SQL manualmente si no usás migraciones
```

4. **Reiniciar servicios**:
```bash
# Backend Flask
systemctl restart flask-app  # O tu método de reinicio

# Celery worker
systemctl restart celery-worker
```

5. **Verificar instalación**:
```bash
# Test de WeasyPrint
python -c "from weasyprint import HTML; print('WeasyPrint OK')"

# Test de Plotly
python -c "import plotly; print('Plotly OK')"
```

6. **Generar reporte de prueba**:
   - Ir al frontend
   - Seleccionar workspace
   - Generar reporte técnico
   - Verificar que se descarga correctamente

---

### Rollback Plan

Si algo falla después del despliegue:

1. **Revertir código**:
```bash
git revert HEAD
# O volver al commit anterior
git checkout <commit-anterior>
```

2. **Revertir migración de BD** (si aplicaste):
```bash
flask db downgrade
```

3. **Cambiar generador a ReportLab** temporalmente:
```python
# En reporting_tasks.py, comentar WeasyPrint y descomentar ReportLab
# from services.reporting.generators.pdf_generator_simple import SimplePDFGenerator
# generator = SimplePDFGenerator()
```

---

## 📝 CHECKLIST FINAL

### Parte 1: Base de Datos ✅
- [ ] Modelo `Report` extendido con todos los campos
- [ ] `ReportRepository` creado y testeado
- [ ] Migración de BD aplicada
- [ ] Tarea Celery guarda reportes en BD
- [ ] Endpoint `/list/<workspace_id>` funcional
- [ ] Endpoint `/download` soporta `report_id`
- [ ] Frontend usa `report_id` para descargar
- [ ] Tests unitarios passing

### Parte 2: WeasyPrint ✅
- [ ] WeasyPrint instalado
- [ ] `WeasyPrintPDFGenerator` creado
- [ ] Template HTML profesional creado
- [ ] PDFs se generan con diseño bonito
- [ ] Colores de severidad correctos
- [ ] Portada profesional
- [ ] Tarea Celery usa WeasyPrint
- [ ] Test end-to-end funcional

### Parte 3: Gráficos ✅
- [ ] Plotly y Kaleido instalados
- [ ] `ChartBuilder` creado
- [ ] Gráficos se generan correctamente
- [ ] PDFs incluyen gráficos
- [ ] Gráficos tienen buena calidad
- [ ] Tests de gráficos passing

### General ✅
- [ ] Todos los tests unitarios passing
- [ ] Tests de integración passing
- [ ] Validación manual completada
- [ ] Documentación actualizada
- [ ] Despliegue exitoso
- [ ] Rollback plan documentado

---

## 🎯 RESUMEN

Este documento proporciona una guía completa para implementar 3 mejoras críticas al módulo de reportería:

1. **Persistencia en BD**: Para mantener historial y permitir re-descarga
2. **WeasyPrint**: Para PDFs profesionales con HTML/CSS
3. **Gráficos Plotly**: Para visualizaciones de calidad

**Tiempo estimado de implementación**:
- Parte 1 (BD): 30-60 minutos
- Parte 2 (WeasyPrint): 2-3 horas
- Parte 3 (Gráficos): 1-2 horas
- Testing y validación: 1 hora
- **Total**: ~5-7 horas

**Beneficios**:
- ✅ Reportes se guardan y son recuperables
- ✅ PDFs mucho más profesionales y presentables
- ✅ Visualizaciones claras para management
- ✅ Sistema más robusto y completo

---

**Autor**: Claude AI  
**Fecha**: 10 Diciembre 2025  
**Versión**: 1.0