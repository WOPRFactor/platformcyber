#!/usr/bin/env python3
"""
Script para ejecutar migración de workspace_logs
================================================

Ejecuta la migración SQL para crear tabla workspace_logs y agregar campo status.
"""

import os
import sys
from sqlalchemy import text

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db


def run_migration():
    """Ejecuta la migración SQL."""
    app = create_app('development')
    
    with app.app_context():
        try:
            print("🔄 Ejecutando migración de workspace_logs...")
            
            # 1. Agregar columna status a workspaces
            print("   Agregando columna status a workspaces...")
            try:
                # Verificar si la columna ya existe
                result = db.session.execute(text("PRAGMA table_info(workspaces);"))
                existing_columns = {row[1] for row in result}
                
                if 'status' not in existing_columns:
                    db.session.execute(text(
                        "ALTER TABLE workspaces ADD COLUMN status VARCHAR(20) DEFAULT 'active';"
                    ))
                    print("   ✓ Columna status agregada")
                else:
                    print("   ✓ Columna status ya existe")
            except Exception as e:
                print(f"   ⚠️  Error agregando columna status: {e}")
            
            # 2. Actualizar workspaces existentes
            print("   Actualizando workspaces existentes...")
            try:
                db.session.execute(text("""
                    UPDATE workspaces 
                    SET status = CASE 
                        WHEN is_active = 1 THEN 'active'
                        ELSE 'archived'
                    END 
                    WHERE status IS NULL OR status = '';
                """))
                print("   ✓ Workspaces actualizados")
            except Exception as e:
                print(f"   ⚠️  Error actualizando workspaces: {e}")
            
            # 3. Crear tabla workspace_logs
            print("   Creando tabla workspace_logs...")
            try:
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS workspace_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workspace_id INTEGER NOT NULL,
                        source VARCHAR(50) NOT NULL,
                        level VARCHAR(10) NOT NULL,
                        message TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        task_id VARCHAR(100),
                        log_metadata TEXT,
                        FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
                    );
                """))
                print("   ✓ Tabla workspace_logs creada")
            except Exception as e:
                if 'already exists' in str(e).lower():
                    print("   ✓ Tabla workspace_logs ya existe")
                else:
                    raise
            
            # 4. Crear índices
            print("   Creando índices...")
            indices = [
                ("idx_workspace_logs_workspace_id", "workspace_logs(workspace_id)"),
                ("idx_workspace_logs_timestamp", "workspace_logs(timestamp)"),
                ("idx_workspace_logs_workspace_timestamp", "workspace_logs(workspace_id, timestamp)"),
                ("idx_workspace_logs_source", "workspace_logs(source)"),
                ("idx_workspace_logs_level", "workspace_logs(level)"),
                ("idx_workspaces_status", "workspaces(status)")
            ]
            
            for idx_name, idx_def in indices:
                try:
                    db.session.execute(text(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_def};"))
                    print(f"   ✓ Índice {idx_name} creado")
                except Exception as e:
                    print(f"   ⚠️  Error creando índice {idx_name}: {e}")
            
            db.session.commit()
            print("\n✅ Migración completada exitosamente")
            
            # Verificar
            print("\n📊 Verificación:")
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='workspace_logs';"))
            if result.fetchone():
                print("   ✓ Tabla workspace_logs existe")
            
            result = db.session.execute(text("PRAGMA table_info(workspaces);"))
            columns = {row[1] for row in result}
            if 'status' in columns:
                print("   ✓ Columna status existe en workspaces")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error ejecutando migración: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    print("=" * 60)
    print("MIGRACIÓN: workspace_logs y campo status")
    print("=" * 60)
    
    success = run_migration()
    
    if success:
        print("\n" + "=" * 60)
        print("✨ Migración finalizada con éxito")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("⚠️  Migración falló - revisar errores")
        print("=" * 60)
        sys.exit(1)

