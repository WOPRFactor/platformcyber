#!/usr/bin/env python3
"""
Script para ejecutar la migración de workspaces
Agrega campos para target principal, scope y fechas del proyecto
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db
from sqlalchemy import text

def run_migration():
    """Ejecuta la migración de workspaces"""
    
    # Crear app context
    app = create_app('development')
    
    # Lista de columnas a agregar (SQLite no soporta IF NOT EXISTS en ALTER TABLE)
    columns_to_add = [
        ("target_domain", "VARCHAR(255)"),
        ("target_ip", "VARCHAR(50)"),
        ("target_type", "VARCHAR(50)"),
        ("in_scope", "TEXT"),
        ("out_of_scope", "TEXT"),
        ("start_date", "DATE"),
        ("end_date", "DATE"),
        ("notes", "TEXT")
    ]
    
    with app.app_context():
        try:
            print("🔄 Ejecutando migración de workspaces...")
            
            # Verificar qué columnas ya existen
            result = db.session.execute(text("""
                PRAGMA table_info(workspaces);
            """))
            existing_columns = {row[1] for row in result}
            
            # Agregar solo las columnas que no existen
            added_count = 0
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    sql = f"ALTER TABLE workspaces ADD COLUMN {column_name} {column_type};"
                    print(f"   Agregando columna: {column_name}")
                    db.session.execute(text(sql))
                    added_count += 1
                else:
                    print(f"   ✓ Columna {column_name} ya existe")
            
            # Crear índices
            print("   Creando índices...")
            try:
                db.session.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_workspaces_target_domain ON workspaces(target_domain);"
                ))
                db.session.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_workspaces_target_type ON workspaces(target_type);"
                ))
            except Exception as idx_error:
                print(f"   ⚠️  Error creando índices (puede ser que ya existan): {idx_error}")
            
            db.session.commit()
            
            print(f"\n✅ Migración completada! ({added_count} columnas nuevas agregadas)")
            print("\n📊 Nuevos campos agregados:")
            print("   - target_domain (VARCHAR 255)")
            print("   - target_ip (VARCHAR 50)")
            print("   - target_type (VARCHAR 50)")
            print("   - in_scope (TEXT)")
            print("   - out_of_scope (TEXT)")
            print("   - start_date (DATE)")
            print("   - end_date (DATE)")
            print("   - notes (TEXT)")
            print("\n🔍 Índices creados:")
            print("   - idx_workspaces_target_domain")
            print("   - idx_workspaces_target_type")
            
            # Verificar las columnas
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'workspaces'
                AND column_name IN (
                    'target_domain', 'target_ip', 'target_type',
                    'in_scope', 'out_of_scope',
                    'start_date', 'end_date', 'notes'
                )
                ORDER BY column_name;
            """))
            
            print("\n✓ Columnas verificadas:")
            for row in result:
                print(f"   - {row[0]}: {row[1]} (nullable: {row[2]})")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error al ejecutar migración: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("MIGRACIÓN DE BASE DE DATOS - WORKSPACES")
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

