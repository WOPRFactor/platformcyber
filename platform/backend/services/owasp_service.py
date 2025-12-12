"""
OWASP Service
=============

Servicio para auditorías OWASP Top 10.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger(__name__)


class OwaspService:
    """Servicio para auditorías OWASP Top 10."""
    
    # OWASP Top 10 2021 Categories
    OWASP_CATEGORIES = {
        'a01_access_control': {
            'name': 'A01:2021 – Broken Access Control',
            'description': 'Restricciones sobre qué usuarios autenticados pueden hacer',
            'tests': ['idor', 'privilege_escalation', 'cors_misconfiguration', 'force_browsing']
        },
        'a02_crypto_failures': {
            'name': 'A02:2021 – Cryptographic Failures',
            'description': 'Fallos relacionados con criptografía',
            'tests': ['weak_ssl', 'weak_cipher', 'sensitive_data_exposure', 'missing_encryption']
        },
        'a03_injection': {
            'name': 'A03:2021 – Injection',
            'description': 'SQL, NoSQL, OS, LDAP injection',
            'tests': ['sql_injection', 'command_injection', 'ldap_injection', 'xml_injection']
        },
        'a04_insecure_design': {
            'name': 'A04:2021 – Insecure Design',
            'description': 'Diseño inseguro de la aplicación',
            'tests': ['missing_rate_limiting', 'insufficient_workflow', 'business_logic_flaws']
        },
        'a05_misconfig': {
            'name': 'A05:2021 – Security Misconfiguration',
            'description': 'Configuraciones de seguridad incorrectas',
            'tests': ['default_credentials', 'directory_listing', 'verbose_errors', 'unnecessary_features']
        },
        'a06_vuln_components': {
            'name': 'A06:2021 – Vulnerable and Outdated Components',
            'description': 'Uso de componentes con vulnerabilidades conocidas',
            'tests': ['outdated_libraries', 'known_cves', 'unsupported_versions']
        },
        'a07_auth_failures': {
            'name': 'A07:2021 – Identification and Authentication Failures',
            'description': 'Fallos en autenticación',
            'tests': ['weak_passwords', 'credential_stuffing', 'session_fixation', 'missing_mfa']
        },
        'a08_integrity_failures': {
            'name': 'A08:2021 – Software and Data Integrity Failures',
            'description': 'Fallos en integridad de software y datos',
            'tests': ['insecure_deserialization', 'unsigned_updates', 'ci_cd_vulnerabilities']
        },
        'a09_logging_failures': {
            'name': 'A09:2021 – Security Logging and Monitoring Failures',
            'description': 'Logging y monitoreo insuficiente',
            'tests': ['insufficient_logging', 'log_injection', 'missing_alerts']
        },
        'a10_ssrf': {
            'name': 'A10:2021 – Server-Side Request Forgery',
            'description': 'SSRF permite acceso a recursos internos',
            'tests': ['ssrf_basic', 'ssrf_cloud_metadata', 'ssrf_internal_network']
        }
    }
    
    def __init__(self):
        """Inicializa el servicio OWASP."""
        self.audits = {}  # En memoria por ahora
        logger.info("✅ OWASP Service inicializado")
    
    def create_audit(
        self,
        target: str,
        workspace_id: int,
        categories: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Crea una nueva auditoría OWASP.
        
        Args:
            target: URL o IP objetivo
            workspace_id: ID del workspace
            categories: Categorías OWASP específicas a auditar (todas si None)
            options: Opciones adicionales
            
        Returns:
            Dict con detalles de la auditoría creada
        """
        audit_id = str(uuid4())
        
        # Si no se especifican categorías, usar todas
        if categories is None:
            categories = list(self.OWASP_CATEGORIES.keys())
        
        audit = {
            'id': audit_id,
            'target': target,
            'workspace_id': workspace_id,
            'status': 'pending',
            'progress': 0,
            'categories': categories,
            'vulnerabilities': {cat: 0 for cat in categories},
            'findings': [],
            'started_at': datetime.now().isoformat(),
            'completed_at': None,
            'options': options or {},
            'created_by': 'admin'  # TODO: Obtener del JWT
        }
        
        self.audits[audit_id] = audit
        logger.info(f"📋 Auditoría OWASP creada: {audit_id} para {target}")
        
        # Logging al workspace
        from utils.workspace_logger import log_to_workspace
        log_to_workspace(
            workspace_id=workspace_id,
            source='OWASP',
            level='INFO',
            message=f"Iniciando auditoría OWASP para {target}",
            metadata={
                'audit_id': audit_id,
                'target': target,
                'categories': categories,
                'categories_count': len(categories)
            }
        )
        
        # En producción, aquí se dispararía tarea Celery
        # from tasks.owasp_tasks import run_owasp_audit
        # run_owasp_audit.delay(audit_id, target, categories, options)
        
        return {
            'success': True,
            'audit': audit
        }
    
    def get_audit(self, audit_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalles de una auditoría.
        
        Args:
            audit_id: ID de la auditoría
            
        Returns:
            Dict con detalles o None si no existe
        """
        audit = self.audits.get(audit_id)
        if audit:
            logger.info(f"📊 Obteniendo auditoría: {audit_id}")
        return audit
    
    def list_audits(
        self,
        workspace_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista auditorías.
        
        Args:
            workspace_id: Filtrar por workspace
            status: Filtrar por estado
            
        Returns:
            Lista de auditorías
        """
        audits = list(self.audits.values())
        
        if workspace_id:
            audits = [a for a in audits if a['workspace_id'] == workspace_id]
        
        if status:
            audits = [a for a in audits if a['status'] == status]
        
        logger.info(f"📋 Listando auditorías: {len(audits)} encontradas")
        return audits
    
    def update_audit_progress(
        self,
        audit_id: str,
        progress: int,
        status: Optional[str] = None
    ) -> bool:
        """
        Actualiza progreso de auditoría.
        
        Args:
            audit_id: ID de la auditoría
            progress: Progreso (0-100)
            status: Nuevo estado (opcional)
            
        Returns:
            True si exitoso, False si no existe
        """
        audit = self.audits.get(audit_id)
        if not audit:
            return False
        
        audit['progress'] = min(100, max(0, progress))
        
        if status:
            audit['status'] = status
            if status == 'completed':
                audit['completed_at'] = datetime.now().isoformat()
        
        logger.info(f"📈 Progreso actualizado: {audit_id} - {progress}%")
        return True
    
    def add_finding(
        self,
        audit_id: str,
        category: str,
        finding: Dict[str, Any]
    ) -> bool:
        """
        Agrega un hallazgo a la auditoría.
        
        Args:
            audit_id: ID de la auditoría
            category: Categoría OWASP (ej: 'a01_access_control')
            finding: Dict con detalles del hallazgo
            
        Returns:
            True si exitoso
        """
        audit = self.audits.get(audit_id)
        if not audit:
            return False
        
        finding_id = str(uuid4())
        full_finding = {
            'id': finding_id,
            'category': category,
            'severity': finding.get('severity', 'medium'),
            'title': finding.get('title', 'Vulnerability Found'),
            'description': finding.get('description', ''),
            'evidence': finding.get('evidence', ''),
            'remediation': finding.get('remediation', ''),
            'cve': finding.get('cve'),
            'cvss': finding.get('cvss'),
            'found_at': datetime.now().isoformat()
        }
        
        audit['findings'].append(full_finding)
        
        # Incrementar contador de vulnerabilidades
        if category in audit['vulnerabilities']:
            audit['vulnerabilities'][category] += 1
        
        logger.info(f"🔍 Hallazgo agregado a {audit_id}: {category}")
        return True
    
    def delete_audit(self, audit_id: str) -> bool:
        """
        Elimina una auditoría.
        
        Args:
            audit_id: ID de la auditoría
            
        Returns:
            True si exitoso
        """
        if audit_id in self.audits:
            del self.audits[audit_id]
            logger.info(f"🗑️  Auditoría eliminada: {audit_id}")
            return True
        return False
    
    def get_category_info(self, category: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de una categoría OWASP.
        
        Args:
            category: ID de categoría (ej: 'a01_access_control')
            
        Returns:
            Dict con info de la categoría
        """
        return self.OWASP_CATEGORIES.get(category)
    
    def get_all_categories(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene todas las categorías OWASP Top 10.
        
        Returns:
            Dict con todas las categorías
        """
        return self.OWASP_CATEGORIES
    
    def simulate_audit(self, audit_id: str) -> bool:
        """
        Simula ejecución de auditoría (para testing).
        
        Args:
            audit_id: ID de la auditoría
            
        Returns:
            True si exitoso
        """
        audit = self.audits.get(audit_id)
        if not audit:
            return False
        
        import random
        
        # Simular cambio de estado
        audit['status'] = 'running'
        audit['progress'] = 50
        
        # Simular algunos hallazgos
        sample_findings = [
            {
                'category': 'a03_injection',
                'severity': 'high',
                'title': 'SQL Injection Detected',
                'description': 'Possible SQL injection in login form',
                'remediation': 'Use parameterized queries'
            },
            {
                'category': 'a07_auth_failures',
                'severity': 'medium',
                'title': 'Weak Password Policy',
                'description': 'No minimum password requirements',
                'remediation': 'Implement strong password policy'
            },
            {
                'category': 'a05_misconfig',
                'severity': 'medium',
                'title': 'Directory Listing Enabled',
                'description': 'Server allows directory browsing',
                'remediation': 'Disable directory listing'
            }
        ]
        
        for finding in random.sample(sample_findings, min(2, len(sample_findings))):
            self.add_finding(audit_id, finding['category'], finding)
        
        # Completar auditoría
        audit['status'] = 'completed'
        audit['progress'] = 100
        audit['completed_at'] = datetime.now().isoformat()
        
        logger.info(f"✅ Auditoría simulada completada: {audit_id}")
        return True

    def preview_audit(
        self,
        target: str,
        workspace_id: int,
        categories: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Preview de una auditoría OWASP (sin ejecutar).
        
        Args:
            target: URL o IP objetivo
            workspace_id: ID del workspace
            categories: Categorías OWASP específicas a auditar
            options: Opciones adicionales
            
        Returns:
            Dict con preview del comando y parámetros
        """
        # Si no se especifican categorías, usar todas
        if categories is None:
            categories = list(self.OWASP_CATEGORIES.keys())
        
        # Construir lista de tests que se ejecutarán
        tests_to_run = []
        for cat in categories:
            cat_info = self.OWASP_CATEGORIES.get(cat)
            if cat_info:
                tests_to_run.extend(cat_info.get('tests', []))
        
        # Construir comando simulado
        command_parts = ['owasp-audit', '--target', target]
        
        if categories and len(categories) < len(self.OWASP_CATEGORIES):
            command_parts.extend(['--categories', ','.join(categories)])
        
        if options:
            for key, value in options.items():
                command_parts.extend([f'--{key}', str(value)])
        
        command_str = ' '.join(command_parts)
        
        # Calcular tiempo estimado (basado en número de categorías)
        estimated_time = len(categories) * 300  # 5 minutos por categoría
        
        return {
            'command': command_parts,
            'command_string': command_str,
            'parameters': {
                'target': target,
                'workspace_id': workspace_id,
                'categories': categories,
                'categories_count': len(categories),
                'options': options or {}
            },
            'estimated_timeout': estimated_time,
            'tests_to_run': list(set(tests_to_run)),
            'tests_count': len(set(tests_to_run)),
            'output_file': f'/workspaces/workspace_{workspace_id}/owasp_audits/{{audit_id}}.json',
            'warnings': [
                'Las auditorías OWASP pueden tomar tiempo considerable',
                'Asegúrate de tener permisos para realizar el escaneo',
                'Algunos tests pueden generar tráfico significativo'
            ],
            'suggestions': [
                'Considera ejecutar categorías específicas primero',
                'Revisa las opciones disponibles para optimizar el tiempo',
                'Verifica que el target esté accesible antes de ejecutar'
            ]
        }


# Singleton
owasp_service = OwaspService()




