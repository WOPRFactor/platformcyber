"""
Files Service for Workspaces
============================

Servicio para operaciones de archivos de workspaces.
"""

import logging
import shutil
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from utils.workspace_filesystem import get_workspace_dir
from repositories.workspace_repository import WorkspaceRepository

logger = logging.getLogger(__name__)


def _format_file_size(size_bytes: int) -> str:
    """Formatea tamaño de archivo en formato legible."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


class WorkspaceFilesService:
    """Servicio para operaciones de archivos de workspaces."""
    
    def __init__(self, workspace_repository: WorkspaceRepository = None):
        """Inicializa el servicio."""
        from repositories.workspace_repository import WorkspaceRepository
        self.workspace_repo = workspace_repository or WorkspaceRepository()
    
    def list_files(
        self,
        workspace_id: int,
        category: Optional[str] = None,
        relative_path: str = ''
    ) -> Optional[Dict[str, Any]]:
        """
        Lista archivos del workspace.
        
        Args:
            workspace_id: ID del workspace
            category: Categoría específica (opcional)
            relative_path: Path relativo para navegar subdirectorios
        
        Returns:
            Dict con lista de archivos o None si no existe el workspace
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        categories = ['recon', 'scans', 'enumeration', 'vuln_scans', 'exploitation', 'postexploit', 'ad_scans', 'cloud_scans']
        
        if category:
            if category not in categories:
                raise ValueError(f'Invalid category. Valid categories: {", ".join(categories)}')
            categories = [category]
        
        workspace_dir = get_workspace_dir(workspace_id, workspace.name)
        files_list = []
        directories_list = []
        
        for cat in categories:
            cat_dir = workspace_dir / cat
            
            if relative_path:
                try:
                    target_dir = (cat_dir / relative_path).resolve()
                    cat_dir_resolved = cat_dir.resolve()
                    target_dir.relative_to(cat_dir_resolved)
                    cat_dir = target_dir
                except (ValueError, OSError):
                    raise ValueError('Invalid path')
            
            if cat_dir.exists() and cat_dir.is_dir():
                for item_path in cat_dir.iterdir():
                    if item_path.is_file():
                        stat = item_path.stat()
                        files_list.append({
                            'name': item_path.name,
                            'category': cat,
                            'path': str(item_path.relative_to(workspace_dir)),
                            'size': stat.st_size,
                            'size_human': _format_file_size(stat.st_size),
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'extension': item_path.suffix,
                            'type': 'file'
                        })
                    elif item_path.is_dir():
                        dir_stat = item_path.stat()
                        file_count = sum(1 for _ in item_path.rglob('*') if _.is_file())
                        directories_list.append({
                            'name': item_path.name,
                            'category': cat,
                            'path': str(item_path.relative_to(workspace_dir)),
                            'modified': datetime.fromtimestamp(dir_stat.st_mtime).isoformat(),
                            'type': 'directory',
                            'file_count': file_count
                        })
        
        all_items = directories_list + files_list
        all_items.sort(key=lambda x: x['modified'], reverse=True)
        
        return {
            'workspace_id': workspace_id,
            'workspace_name': workspace.name,
            'total_files': len(files_list),
            'total_directories': len(directories_list),
            'current_path': relative_path,
            'items': all_items,
            'files': files_list,
            'directories': directories_list
        }
    
    def get_file(self, workspace_id: int, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene contenido de un archivo.
        
        Args:
            workspace_id: ID del workspace
            file_path: Ruta relativa del archivo
        
        Returns:
            Dict con contenido del archivo o None si no existe
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        workspace_dir = get_workspace_dir(workspace_id, workspace.name)
        full_path = workspace_dir / file_path
        
        try:
            full_path.resolve().relative_to(workspace_dir.resolve())
        except ValueError:
            raise ValueError('Invalid file path')
        
        if not full_path.exists() or not full_path.is_file():
            return None
        
        try:
            content = full_path.read_text(encoding='utf-8', errors='replace')
            return {
                'workspace_id': workspace_id,
                'file_path': file_path,
                'file_name': full_path.name,
                'size': full_path.stat().st_size,
                'content': content,
                'is_binary': False
            }
        except UnicodeDecodeError:
            return {
                'workspace_id': workspace_id,
                'file_path': file_path,
                'file_name': full_path.name,
                'size': full_path.stat().st_size,
                'content': None,
                'is_binary': True,
                'message': 'File is binary. Use ?download=true to download it.'
            }
    
    def delete_file(self, workspace_id: int, file_path: str) -> bool:
        """
        Elimina un archivo.
        
        Args:
            workspace_id: ID del workspace
            file_path: Ruta relativa del archivo
        
        Returns:
            True si se eliminó, False si no existe
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return False
        
        workspace_dir = get_workspace_dir(workspace_id, workspace.name)
        full_path = workspace_dir / file_path
        
        try:
            full_path.resolve().relative_to(workspace_dir.resolve())
        except ValueError:
            raise ValueError('Invalid file path')
        
        if not full_path.exists():
            return False
        
        if full_path.is_file():
            full_path.unlink()
        elif full_path.is_dir():
            shutil.rmtree(full_path)
        else:
            raise ValueError('Path is not a file or directory')
        
        return True
    
    def delete_all_files(self, workspace_id: int, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Elimina todos los archivos del workspace.
        
        Args:
            workspace_id: ID del workspace
            category: Categoría específica (opcional)
        
        Returns:
            Dict con estadísticas de eliminación
        """
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        workspace_dir = get_workspace_dir(workspace_id, workspace.name)
        categories = ['recon', 'scans', 'enumeration', 'vuln_scans', 'exploitation', 'postexploit', 'ad_scans', 'cloud_scans']
        
        if category:
            if category not in categories:
                raise ValueError(f'Invalid category')
            categories = [category]
        
        deleted_files = 0
        deleted_dirs = 0
        
        for cat in categories:
            cat_dir = workspace_dir / cat
            if cat_dir.exists() and cat_dir.is_dir():
                for item in cat_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                        deleted_files += 1
                    elif item.is_dir():
                        shutil.rmtree(item)
                        deleted_dirs += 1
        
        return {
            'deleted_files': deleted_files,
            'deleted_directories': deleted_dirs,
            'category': category or 'all'
        }


