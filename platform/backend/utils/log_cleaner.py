"""
Log Cleaner Utility
==================

Utilidad para limpiar archivos de log manteniendo solo las últimas horas.
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def clean_log_file(
    log_file_path: str,
    hours_to_keep: int = 24,
    dry_run: bool = False
) -> dict:
    """
    Limpia un archivo de log manteniendo solo las últimas N horas.
    
    Args:
        log_file_path: Ruta al archivo de log
        hours_to_keep: Número de horas a mantener (default: 24)
        dry_run: Si True, solo muestra qué se eliminaría sin hacer cambios
    
    Returns:
        dict: Estadísticas de la limpieza
    """
    log_path = Path(log_file_path)
    
    if not log_path.exists():
        logger.warning(f"Archivo de log no existe: {log_file_path}")
        return {
            'success': False,
            'error': 'File not found',
            'original_size': 0,
            'new_size': 0,
            'lines_removed': 0,
            'lines_kept': 0
        }
    
    # Obtener tamaño original
    original_size = log_path.stat().st_size
    
    # Calcular timestamp de corte
    cutoff_time = datetime.now() - timedelta(hours=hours_to_keep)
    
    # Leer archivo
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        logger.error(f"Error leyendo archivo de log: {e}")
        return {
            'success': False,
            'error': str(e),
            'original_size': original_size,
            'new_size': 0,
            'lines_removed': 0,
            'lines_kept': 0
        }
    
    # Patrón para extraer timestamp de las líneas de log
    # Formato esperado: "2025-11-27 07:43:12 - ..."
    timestamp_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})')
    
    kept_lines = []
    removed_count = 0
    
    for line in lines:
        # Intentar extraer timestamp
        match = timestamp_pattern.match(line)
        if match:
            try:
                date_str = match.group(1)
                time_str = match.group(2)
                line_timestamp = datetime.strptime(
                    f"{date_str} {time_str}",
                    "%Y-%m-%d %H:%M:%S"
                )
                
                # Mantener línea si está dentro del rango
                if line_timestamp >= cutoff_time:
                    kept_lines.append(line)
                else:
                    removed_count += 1
            except ValueError:
                # Si no se puede parsear el timestamp, mantener la línea
                # (puede ser una línea de formato diferente)
                kept_lines.append(line)
        else:
            # Si no tiene timestamp al inicio, mantener la línea
            # (puede ser continuación de una línea anterior)
            kept_lines.append(line)
    
    # Si no hay líneas para mantener, mantener al menos las últimas 100
    if len(kept_lines) == 0 and len(lines) > 0:
        kept_lines = lines[-100:]
        removed_count = len(lines) - 100
        logger.warning("No se encontraron líneas con timestamp válido, manteniendo últimas 100 líneas")
    
    # Escribir archivo limpio
    if not dry_run:
        try:
            # Crear backup temporal
            backup_path = log_path.with_suffix('.log.backup')
            if backup_path.exists():
                backup_path.unlink()
            
            # Escribir líneas mantenidas
            with open(log_path, 'w', encoding='utf-8') as f:
                f.writelines(kept_lines)
            
            # Obtener nuevo tamaño
            new_size = log_path.stat().st_size
            
            logger.info(
                f"Log limpiado: {log_file_path}\n"
                f"  Tamaño original: {original_size / (1024*1024):.2f} MB\n"
                f"  Tamaño nuevo: {new_size / (1024*1024):.2f} MB\n"
                f"  Líneas mantenidas: {len(kept_lines)}\n"
                f"  Líneas eliminadas: {removed_count}"
            )
            
            return {
                'success': True,
                'original_size': original_size,
                'new_size': new_size,
                'lines_removed': removed_count,
                'lines_kept': len(kept_lines),
                'hours_kept': hours_to_keep
            }
        except Exception as e:
            logger.error(f"Error escribiendo archivo de log limpio: {e}")
            return {
                'success': False,
                'error': str(e),
                'original_size': original_size,
                'new_size': 0,
                'lines_removed': 0,
                'lines_kept': 0
            }
    else:
        # Dry run: solo mostrar estadísticas
        logger.info(
            f"DRY RUN - Log a limpiar: {log_file_path}\n"
            f"  Tamaño actual: {original_size / (1024*1024):.2f} MB\n"
            f"  Líneas a mantener: {len(kept_lines)}\n"
            f"  Líneas a eliminar: {removed_count}\n"
            f"  Horas a mantener: {hours_to_keep}"
        )
        return {
            'success': True,
            'dry_run': True,
            'original_size': original_size,
            'new_size': 0,
            'lines_removed': removed_count,
            'lines_kept': len(kept_lines),
            'hours_kept': hours_to_keep
        }


def clean_backend_logs(hours_to_keep: int = 24, dry_run: bool = False) -> dict:
    """
    Limpia los logs del backend.
    
    Limpia TODOS los archivos backend.log encontrados:
    - platform/backend/logs/backend.log
    - platform/backend/backend.log
    - logs/backend.log (directorio raíz del proyecto)
    
    Args:
        hours_to_keep: Horas a mantener (default: 24)
        dry_run: Si True, solo muestra qué se eliminaría
    
    Returns:
        dict: Resultado de la limpieza (combinado de todos los archivos)
    """
    results = []
    
    # Ruta al archivo de log del backend (directorio backend/logs/)
    backend_dir = Path(__file__).parent.parent
    log_files = [
        backend_dir / 'logs' / 'backend.log',
        backend_dir / 'backend.log',
        # También buscar en el directorio raíz del proyecto (2 niveles arriba desde backend)
        backend_dir.parent.parent / 'logs' / 'backend.log'
    ]
    
    for log_file in log_files:
        if log_file.exists():
            result = clean_log_file(str(log_file), hours_to_keep, dry_run)
            results.append({
                'file': str(log_file),
                'result': result
            })
    
    # Retornar resultado combinado
    if results:
        total_original = sum(r['result'].get('original_size', 0) for r in results)
        total_new = sum(r['result'].get('new_size', 0) for r in results)
        total_removed = sum(r['result'].get('lines_removed', 0) for r in results)
        
        return {
            'success': all(r['result'].get('success', False) for r in results),
            'files_cleaned': len(results),
            'total_original_size': total_original,
            'total_new_size': total_new,
            'total_lines_removed': total_removed,
            'details': results
        }
    else:
        return {
            'success': False,
            'error': 'No backend.log files found',
            'files_cleaned': 0
        }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Limpia archivos de log manteniendo solo las últimas horas')
    parser.add_argument('--file', type=str, help='Ruta al archivo de log')
    parser.add_argument('--hours', type=int, default=24, help='Horas a mantener (default: 24)')
    parser.add_argument('--dry-run', action='store_true', help='Solo mostrar qué se eliminaría')
    parser.add_argument('--backend', action='store_true', help='Limpiar log del backend')
    
    args = parser.parse_args()
    
    # Configurar logging básico
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    if args.backend:
        result = clean_backend_logs(args.hours, args.dry_run)
    elif args.file:
        result = clean_log_file(args.file, args.hours, args.dry_run)
    else:
        parser.print_help()
        exit(1)
    
    if result.get('success'):
        print(f"✅ Limpieza completada exitosamente")
    else:
        print(f"❌ Error en limpieza: {result.get('error', 'Unknown error')}")
        exit(1)





