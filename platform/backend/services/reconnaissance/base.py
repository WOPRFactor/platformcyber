"""
Base Reconnaissance Service
===========================

Clase base con métodos comunes para todos los servicios de reconocimiento.
"""

import logging
from pathlib import Path

from repositories import ScanRepository
from .executors import ReconnaissanceExecutor

logger = logging.getLogger(__name__)


class BaseReconnaissanceService:
    """Clase base con funcionalidad común para servicios de reconocimiento."""
    
    def __init__(self, scan_repository: ScanRepository = None):
        """Inicializa el servicio base."""
        self.scan_repo = scan_repository or ScanRepository()
        from utils.workspace_filesystem import PROJECT_TMP_DIR
        self.output_dir = PROJECT_TMP_DIR / 'recon'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.executor = ReconnaissanceExecutor(self.scan_repo)
    
    def _get_output_file(self, scan_id: int, tool: str, category: str = 'recon') -> Path:
        """
        Obtiene path del archivo de salida.
        
        Args:
            scan_id: ID del escaneo
            tool: Nombre de la herramienta
            category: Categoría del escaneo (recon, scans, enumeration, etc.)
        
        Returns:
            Path del archivo de salida
        """
        from utils.workspace_filesystem import get_workspace_output_dir_from_scan
        
        workspace_output_dir = get_workspace_output_dir_from_scan(scan_id, category)
        
        extensions = {
            'theHarvester': '.json',
            'dnsrecon': '.json',
            'shodan': '.json',
            'gitleaks': '.json',
            'trufflehog': '.json',
            'hunter_io': '.json',
            'censys': '.json'
        }
        ext = extensions.get(tool, '.txt')
        return workspace_output_dir / f'{tool}_{scan_id}{ext}'
    
    def _get_workspace_output_dir(self, scan_id: int, category: str = 'recon') -> Path:
        """
        Obtiene directorio de output del workspace para un scan.
        
        Args:
            scan_id: ID del escaneo
            category: Categoría del escaneo (recon, scans, enumeration, etc.)
        
        Returns:
            Path al directorio de output del workspace
        """
        from utils.workspace_filesystem import get_workspace_output_dir_from_scan
        return get_workspace_output_dir_from_scan(scan_id, category)
    
    def _execute_scan(
        self,
        scan_id: int,
        command: list,
        output_file: str,
        scan_type: str
    ) -> None:
        """
        Ejecuta scan en thread separado.
        
        Args:
            scan_id: ID del escaneo
            command: Comando a ejecutar
            output_file: Archivo de salida
            scan_type: Tipo de scan para logging
        """
        self.executor.execute_scan(scan_id, command, output_file, scan_type)
