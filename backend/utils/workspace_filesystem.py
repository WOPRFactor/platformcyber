"""
Workspace Filesystem Utilities
===============================

Utilidades para gestionar directorios de archivos por workspace.
Cada workspace tiene su propio directorio con subdirectorios por categoría.
"""

import re
import logging
from pathlib import Path
from typing import Optional
import os

logger = logging.getLogger(__name__)

# Directorio base para workspaces (configurable por variable de entorno)
# Default: usar directorio en el proyecto si no hay permisos para /workspaces
_default_base = Path('/workspaces')
if not _default_base.exists():
    # Intentar crear, si falla usar directorio en el proyecto
    try:
        _default_base.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError):
        # Fallback a directorio en el proyecto
        _default_base = Path(__file__).parent.parent.parent / 'workspaces'
        _default_base.mkdir(parents=True, exist_ok=True)

WORKSPACES_BASE_DIR = Path(os.getenv('WORKSPACES_BASE_DIR', str(_default_base)))

# Directorio temporal del proyecto (en lugar de /tmp para evitar llenar tmpfs)
# Ubicado en el proyecto para tener espacio en disco
PROJECT_TMP_DIR = Path(__file__).parent.parent.parent / 'tmp'
PROJECT_TMP_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_workspace_name(name: str) -> str:
    """
    Sanitiza nombre de workspace para usar en filesystem.
    
    Convierte nombres como "Cliente ABC" a "cliente_abc" para usar
    como nombre de directorio seguro.
    
    Args:
        name: Nombre del workspace
    
    Returns:
        Nombre sanitizado seguro para filesystem
    
    Ejemplos:
        "Cliente ABC" → "cliente_abc"
        "Proyecto-2024" → "proyecto-2024"
        "Test/Dev" → "test_dev"
        "Workspace #1" → "workspace_1"
    """
    if not name:
        return "workspace_unnamed"
    
    # Convertir a lowercase
    safe = name.lower()
    
    # Reemplazar espacios y caracteres especiales por underscore
    safe = re.sub(r'[^\w\-_]', '_', safe)
    
    # Reemplazar múltiples underscores por uno solo
    safe = re.sub(r'_+', '_', safe)
    
    # Eliminar underscores al inicio y final
    safe = safe.strip('_')
    
    # Limitar longitud (máximo 50 caracteres)
    safe = safe[:50]
    
    # Si quedó vacío, usar nombre por defecto
    if not safe:
        safe = "workspace_unnamed"
    
    return safe


def get_workspace_dir(workspace_id: int, workspace_name: str) -> Path:
    """
    Obtiene o crea directorio principal para un workspace.
    
    Args:
        workspace_id: ID del workspace
        workspace_name: Nombre del workspace
    
    Returns:
        Path al directorio principal del workspace
    
    Ejemplo:
        get_workspace_dir(1, "Cliente ABC")
        → Path('/workspaces/cliente_abc')
    """
    safe_name = sanitize_workspace_name(workspace_name)
    workspace_dir = WORKSPACES_BASE_DIR / safe_name
    
    # Crear directorio si no existe
    try:
        workspace_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Workspace directory: {workspace_dir}")
    except PermissionError as e:
        logger.error(f"Sin permisos para crear directorio {workspace_dir}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error creando directorio {workspace_dir}: {e}")
        raise
    
    return workspace_dir


def get_workspace_output_dir(
    workspace_id: int,
    workspace_name: str,
    category: str
) -> Path:
    """
    Obtiene directorio de output para una categoría específica de un workspace.
    
    Crea el directorio si no existe.
    
    Args:
        workspace_id: ID del workspace
        workspace_name: Nombre del workspace
        category: Categoría (recon, scans, enumeration, vuln_scans, 
                 exploitation, postexploit, ad_scans, cloud_scans)
    
    Returns:
        Path al directorio de output de la categoría
    
    Ejemplo:
        get_workspace_output_dir(1, "Cliente ABC", "recon")
        → Path('/workspaces/cliente_abc/recon')
    """
    workspace_dir = get_workspace_dir(workspace_id, workspace_name)
    output_dir = workspace_dir / category
    
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Output directory for {category}: {output_dir}")
    except PermissionError as e:
        logger.error(f"Sin permisos para crear directorio {output_dir}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error creando directorio {output_dir}: {e}")
        raise
    
    return output_dir


def get_workspace_output_dir_from_scan(scan_id: int, category: str) -> Path:
    """
    Obtiene directorio de output desde un scan_id.
    
    Busca el workspace asociado al scan y retorna el directorio
    de la categoría especificada.
    
    Args:
        scan_id: ID del scan
        category: Categoría (recon, scans, enumeration, etc.)
    
    Returns:
        Path al directorio de output, o Path('{proyecto}/tmp/{category}') como fallback
        si no se encuentra el workspace
    """
    try:
        from repositories import ScanRepository
        
        scan_repo = ScanRepository()
        scan = scan_repo.find_by_id(scan_id)
        
        if not scan or not scan.workspace:
            logger.warning(f"Scan {scan_id} no tiene workspace, usando {PROJECT_TMP_DIR}/{category}")
            fallback_dir = PROJECT_TMP_DIR / category
            fallback_dir.mkdir(parents=True, exist_ok=True)
            return fallback_dir
        
        workspace = scan.workspace
        return get_workspace_output_dir(workspace.id, workspace.name, category)
        
    except Exception as e:
        logger.error(f"Error obteniendo workspace directory para scan {scan_id}: {e}")
        # Fallback a directorio tmp del proyecto
        fallback_dir = PROJECT_TMP_DIR / category
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return fallback_dir


def create_workspace_directory_structure(workspace_id: int, workspace_name: str) -> Path:
    """
    Crea estructura completa de directorios para un workspace.
    
    Crea todos los subdirectorios necesarios:
    - recon
    - scans
    - enumeration
    - vuln_scans
    - exploitation
    - postexploit
    - ad_scans
    - cloud_scans
    
    Args:
        workspace_id: ID del workspace
        workspace_name: Nombre del workspace
    
    Returns:
        Path al directorio principal del workspace
    """
    workspace_dir = get_workspace_dir(workspace_id, workspace_name)
    
    # Categorías estándar
    categories = [
        'recon',
        'scans',
        'enumeration',
        'vuln_scans',
        'exploitation',
        'postexploit',
        'ad_scans',
        'cloud_scans'
    ]
    
    # Crear todos los subdirectorios
    for category in categories:
        category_dir = workspace_dir / category
        try:
            category_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Error creando subdirectorio {category}: {e}")
    
    logger.info(f"Estructura de directorios creada para workspace {workspace_id}: {workspace_dir}")
    return workspace_dir


def archive_workspace_directory(workspace_id: int, workspace_name: str, archive_dir: Optional[Path] = None) -> Path:
    """
    Archiva directorio de workspace moviéndolo a directorio de archivo.
    
    Args:
        workspace_id: ID del workspace
        workspace_name: Nombre del workspace
        archive_dir: Directorio de archivo (default: /archived/workspaces)
    
    Returns:
        Path al directorio archivado
    """
    workspace_dir = get_workspace_dir(workspace_id, workspace_name)
    
    if not workspace_dir.exists():
        logger.warning(f"Workspace directory {workspace_dir} no existe")
        return workspace_dir
    
    if archive_dir is None:
        archive_dir = Path('/archived/workspaces')
    
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Mover directorio
    import shutil
    archived_path = archive_dir / workspace_dir.name
    shutil.move(str(workspace_dir), str(archived_path))
    
    logger.info(f"Workspace {workspace_id} archivado en {archived_path}")
    return archived_path


def delete_workspace_directory(workspace_id: int, workspace_name: str) -> bool:
    """
    Elimina completamente el directorio de un workspace.
    
    Elimina el directorio y todo su contenido de forma permanente.
    Esta operación es irreversible.
    
    Args:
        workspace_id: ID del workspace
        workspace_name: Nombre del workspace
    
    Returns:
        True si se eliminó exitosamente, False si no existía o hubo error
    
    Raises:
        PermissionError: Si no hay permisos para eliminar
        OSError: Si hay un error del sistema al eliminar
    """
    try:
        workspace_dir = get_workspace_dir(workspace_id, workspace_name)
        
        if not workspace_dir.exists():
            logger.info(f"Workspace directory {workspace_dir} no existe, nada que eliminar")
            return False
        
        # Eliminar directorio completo con todo su contenido
        import shutil
        shutil.rmtree(str(workspace_dir))
        
        logger.info(f"Workspace directory {workspace_dir} eliminado exitosamente")
        return True
        
    except PermissionError as e:
        logger.error(f"Sin permisos para eliminar directorio {workspace_dir}: {e}")
        raise
    except OSError as e:
        logger.error(f"Error del sistema al eliminar directorio {workspace_dir}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado eliminando directorio del workspace {workspace_id}: {e}")
        raise

