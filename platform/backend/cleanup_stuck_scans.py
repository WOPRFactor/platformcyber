#!/usr/bin/env python3
"""
Script de Limpieza de Scans Colgados
=====================================

Identifica y limpia scans que están en estado "running" por más tiempo del esperado.

Uso:
    python cleanup_stuck_scans.py [--hours HOURS] [--dry-run]
    
Ejemplos:
    # Limpiar scans colgados por más de 2 horas (default)
    python cleanup_stuck_scans.py
    
    # Limpiar scans colgados por más de 6 horas
    python cleanup_stuck_scans.py --hours 6
    
    # Ver qué scans se limpiarían sin hacer cambios
    python cleanup_stuck_scans.py --dry-run
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app import create_app
from models import db, Scan
from utils.workspace_logger import log_to_workspace


def cleanup_stuck_scans(hours_threshold: int = 2, dry_run: bool = False):
    """
    Limpia scans que están en estado 'running' por más del tiempo especificado.
    
    Args:
        hours_threshold: Horas mínimas que un scan debe estar en 'running' para considerarse colgado
        dry_run: Si True, solo muestra qué scans se limpiarían sin hacer cambios
    """
    app = create_app('development')
    
    with app.app_context():
        # Calcular el tiempo límite
        time_limit = datetime.utcnow() - timedelta(hours=hours_threshold)
        
        # Buscar scans colgados
        stuck_scans = Scan.query.filter(
            Scan.status == 'running',
            Scan.started_at < time_limit
        ).all()
        
        if not stuck_scans:
            print(f"✅ No se encontraron scans colgados (más de {hours_threshold} horas)")
            return
        
        print(f"🔍 Encontrados {len(stuck_scans)} scans colgados (más de {hours_threshold} horas):\n")
        
        for scan in stuck_scans:
            hours_stuck = (datetime.utcnow() - scan.started_at).total_seconds() / 3600
            print(f"  - Scan ID: {scan.id}")
            print(f"    Tipo: {scan.scan_type}")
            print(f"    Target: {scan.target}")
            print(f"    Iniciado: {scan.started_at}")
            print(f"    Tiempo colgado: {hours_stuck:.1f} horas")
            print(f"    Workspace ID: {scan.workspace_id}")
            print()
        
        if dry_run:
            print("🔍 DRY RUN: No se realizaron cambios. Ejecuta sin --dry-run para limpiar.")
            return
        
        # Confirmar antes de limpiar
        print(f"⚠️  Se marcarán {len(stuck_scans)} scans como 'failed'")
        response = input("¿Continuar? (s/N): ").strip().lower()
        
        if response != 's':
            print("❌ Operación cancelada")
            return
        
        # Limpiar scans
        cleaned_count = 0
        for scan in stuck_scans:
            try:
                error_msg = f"Scan abandoned - stuck in 'running' for {hours_stuck:.1f} hours"
                scan.status = 'failed'
                scan.error = error_msg
                scan.completed_at = datetime.utcnow()
                
                db.session.commit()
                
                # Log al workspace
                log_to_workspace(
                    workspace_id=scan.workspace_id,
                    source='CLEANUP',
                    level='WARNING',
                    message=f"Scan {scan.id} ({scan.scan_type}) marcado como failed - estaba colgado",
                    metadata={
                        'scan_id': scan.id,
                        'scan_type': scan.scan_type,
                        'target': scan.target,
                        'hours_stuck': round(hours_stuck, 1)
                    }
                )
                
                cleaned_count += 1
                print(f"✅ Scan {scan.id} limpiado")
                
            except Exception as e:
                print(f"❌ Error limpiando scan {scan.id}: {e}")
                db.session.rollback()
        
        print(f"\n✅ Limpieza completada: {cleaned_count}/{len(stuck_scans)} scans limpiados")


def main():
    parser = argparse.ArgumentParser(
        description='Limpia scans que están colgados en estado "running"'
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=2,
        help='Horas mínimas que un scan debe estar en "running" para considerarse colgado (default: 2)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Solo muestra qué scans se limpiarían sin hacer cambios'
    )
    
    args = parser.parse_args()
    
    cleanup_stuck_scans(
        hours_threshold=args.hours,
        dry_run=args.dry_run
    )


if __name__ == '__main__':
    main()




