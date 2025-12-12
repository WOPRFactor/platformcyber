"""
File Scanner
============

Escanea y descubre archivos de resultados en un workspace.
Organiza archivos por categorías y respeta límites de seguridad.
"""

from pathlib import Path
from typing import Dict, List
import logging
from utils.workspace_filesystem import get_workspace_dir
from ..config import (
    MAX_FILES_PER_CATEGORY,
    MAX_TOTAL_FILES,
    SUPPORTED_CATEGORIES
)


class FileScanner:
    """
    Escanea y descubre archivos de resultados en un workspace.
    
    Organiza archivos por categorías y aplica límites para prevenir
    procesamiento excesivo de archivos.
    """
    
    def __init__(self):
        """Inicializa el scanner con logger."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def scan_workspace(
        self, 
        workspace_id: int, 
        workspace_name: str
    ) -> Dict[str, List[Path]]:
        """
        Escanea un workspace y retorna archivos organizados por categoría.
        
        Args:
            workspace_id: ID del workspace
            workspace_name: Nombre del workspace
            
        Returns:
            Diccionario con categorías como keys y listas de Path como values
            Ejemplo: {
                'recon': [Path('subfinder_123.txt'), Path('amass_124.txt')],
                'scans': [Path('nmap_456.xml')],
                'vuln_scans': [Path('nuclei_789.jsonl'), Path('nikto_790.json')]
            }
        """
        files_by_category = {}
        
        try:
            # Obtener directorio del workspace
            workspace_dir = get_workspace_dir(workspace_id, workspace_name)
            
            # Validar que workspace_name no contenga path traversal
            if not self._is_safe_workspace_name(workspace_name):
                self.logger.error(
                    f"Invalid workspace name (potential path traversal): {workspace_name}"
                )
                return files_by_category
            
            if not workspace_dir.exists():
                self.logger.warning(
                    f"Workspace directory not found: {workspace_dir}"
                )
                return files_by_category
            
            self.logger.info(f"Scanning workspace directory: {workspace_dir}")
            
            total_files_found = 0
            
            # Escanear cada categoría
            for category in SUPPORTED_CATEGORIES:
                category_dir = workspace_dir / category
                
                if not category_dir.exists():
                    self.logger.debug(
                        f"Category directory not found: {category_dir}"
                    )
                    continue
                
                # Buscar todos los archivos (no directorios)
                files = self._scan_category_directory(category_dir)
                
                # Aplicar límite por categoría
                if len(files) > MAX_FILES_PER_CATEGORY:
                    self.logger.warning(
                        f"Category {category} has {len(files)} files, "
                        f"limiting to {MAX_FILES_PER_CATEGORY}"
                    )
                    files = files[:MAX_FILES_PER_CATEGORY]
                
                if files:
                    files_by_category[category] = files
                    total_files_found += len(files)
                    self.logger.info(
                        f"Found {len(files)} files in {category}"
                    )
                
                # Verificar límite total
                if total_files_found >= MAX_TOTAL_FILES:
                    self.logger.warning(
                        f"Reached max total files limit ({MAX_TOTAL_FILES}), "
                        "stopping scan"
                    )
                    break
            
            self.logger.info(f"Total files found: {total_files_found}")
            
        except Exception as e:
            self.logger.error(f"Error scanning workspace: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        return files_by_category
    
    def _scan_category_directory(self, category_dir: Path) -> List[Path]:
        """
        Escanea un directorio de categoría y retorna lista de archivos.
        
        Busca archivos directamente en el directorio y también en
        subdirectorios (algunos tools generan directorios, ej: sqlmap).
        
        Args:
            category_dir: Path al directorio de la categoría
            
        Returns:
            Lista de Paths a archivos encontrados
        """
        files = []
        
        try:
            # Obtener el workspace_dir como base para validación
            workspace_dir = category_dir.parent
            
            for item in category_dir.iterdir():
                if item.is_file():
                    # Validar path traversal
                    if self._is_safe_path(item, workspace_dir):
                        files.append(item)
                elif item.is_dir():
                    # Algunos tools generan directorios (ej: sqlmap)
                    # Buscar archivos dentro
                    for subitem in item.rglob('*'):
                        if subitem.is_file():
                            # Validar path traversal
                            if self._is_safe_path(subitem, workspace_dir):
                                files.append(subitem)
                            else:
                                self.logger.warning(
                                    f"Skipping file outside workspace: {subitem}"
                                )
        except Exception as e:
            self.logger.error(
                f"Error scanning category directory {category_dir}: {e}"
            )
        
        return files
    
    def _is_safe_path(self, file_path: Path, base_dir: Path) -> bool:
        """
        Valida que un path no salga del directorio base (path traversal prevention).
        
        Args:
            file_path: Path al archivo a validar
            base_dir: Directorio base (workspace)
            
        Returns:
            True si el path es seguro, False si intenta path traversal
        """
        try:
            # Resolver paths absolutos
            file_abs = file_path.resolve()
            base_abs = base_dir.resolve()
            
            # Verificar que el archivo esté dentro del base_dir
            # Usar relative_to para verificar que es subdirectorio
            file_abs.relative_to(base_abs)
            return True
        except ValueError:
            # ValueError significa que no es subdirectorio (path traversal)
            return False
        except Exception as e:
            self.logger.error(f"Error validating path {file_path}: {e}")
            return False
    
    def _is_safe_workspace_name(self, workspace_name: str) -> bool:
        """
        Valida que el nombre del workspace no contenga caracteres peligrosos.
        
        Args:
            workspace_name: Nombre del workspace a validar
            
        Returns:
            True si el nombre es seguro, False si contiene caracteres peligrosos
        """
        if not workspace_name:
            return False
        
        # Caracteres peligrosos para path traversal
        dangerous_chars = ['..', '/', '\\', '\x00']
        
        for char in dangerous_chars:
            if char in workspace_name:
                return False
        
        return True
