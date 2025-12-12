#!/usr/bin/env python3
"""
Script para ejecutar la migración de reports para V2
Agrega campos para reportería avanzada (metadata, risk score, versionado, etc.)
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db
from sqlalchemy import text

def run_migration():
    """Ejecuta la migración de reports para V2"""
    
    # Crear app context
    app = create_app('development')
    
    # Lista de columnas a agregar
    columns_to_add = [
        # Versionado
        ("version", "INTEGER DEFAULT 1 NOT NULL"),
        ("is_latest", "BOOLEAN DEFAULT 1 NOT NULL"),
        
        # File security
        ("file_hash", "VARCHAR(64)"),
        
        # Metadata del contenido
        ("total_findings", "INTEGER DEFAULT 0"),
        ("critical_count", "INTEGER DEFAULT 0"),
        ("high_count", "INTEGER DEFAULT 0"),
        ("medium_count", "INTEGER DEFAULT 0"),
        ("low_count", "INTEGER DEFAULT 0"),
        ("info_count", "INTEGER DEFAULT 0"),
        ("risk_score", "FLOAT"),
        
        # Metadata de procesamiento
        ("files_processed", "INTEGER DEFAULT 0"),
        ("tools_used", "TEXT"),  # JSON en SQLite
        ("generation_time_seconds", "FLOAT"),
        
        # Error tracking
        ("error_message", "TEXT")
    ]
    
    with app.app_context():
        try:
            print("🔄 Ejecutando migración de reports V2...")
            
            # Verificar qué columnas ya existen
            result = db.session.execute(text("""
                PRAGMA table_info(reports);
            """))
            existing_columns = {row[1] for row in result}
            
            # Agregar solo las columnas que no existen
            added_count = 0
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    sql = f"ALTER TABLE reports ADD COLUMN {column_name} {column_type};"
                    print(f"   Agregando columna: {column_name}")
                    db.session.execute(text(sql))
                    added_count += 1
                else:
                    print(f"   ✓ Columna {column_name} ya existe")
            
            # Crear índices
            print("   Creando índices...")
            try:
                db.session.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_reports_workspace_type ON reports(workspace_id, report_type);"
                ))
                db.session.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at DESC);"
                ))
                db.session.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);"
                ))
                db.session.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_reports_is_latest ON reports(is_latest) WHERE is_latest = 1;"
                ))
            except Exception as idx_error:
                print(f"   ⚠️  Error creando índices (puede ser que ya existan): {idx_error}")
            
            db.session.commit()
            
            print(f"\n✅ Migración completada! ({added_count} columnas nuevas agregadas)")
            print("\n📊 Nuevos campos agregados:")
            print("   🔢 Versionado:")
            print("      - version (INTEGER)")
            print("      - is_latest (BOOLEAN)")
            print("   🔒 Seguridad:")
            print("      - file_hash (VARCHAR 64)")
            print("   📈 Metadata de Contenido:")
            print("      - total_findings (INTEGER)")
            print("      - critical_count (INTEGER)")
            print("      - high_count (INTEGER)")
            print("      - medium_count (INTEGER)")
            print("      - low_count (INTEGER)")
            print("      - info_count (INTEGER)")
            print("      - risk_score (FLOAT)")
            print("   ⚙️  Metadata de Procesamiento:")
            print("      - files_processed (INTEGER)")
            print("      - tools_used (TEXT/JSON)")
            print("      - generation_time_seconds (FLOAT)")
            print("   ❌ Error Tracking:")
            print("      - error_message (TEXT)")
            print("\n🔍 Índices creados:")
            print("   - idx_reports_workspace_type")
            print("   - idx_reports_created_at")
            print("   - idx_reports_status")
            print("   - idx_reports_is_latest")
            
            # Verificar columnas finales
            result = db.session.execute(text("""
                PRAGMA table_info(reports);
            """))
            
            print("\n✓ Estructura final de la tabla 'reports':")
            for row in result:
                col_id, col_name, col_type, not_null, default_val, pk = row
                nullable = "NOT NULL" if not_null else "NULLABLE"
                default = f" DEFAULT {default_val}" if default_val else ""
                print(f"   - {col_name}: {col_type} ({nullable}){default}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error al ejecutar migración: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("MIGRACIÓN DE BASE DE DATOS - REPORTS V2")
    print("=" * 60)
    
    success = run_migration()
    
    if success:
        print("\n" + "=" * 60)
        print("✨ Migración finalizada con éxito")
        print("=" * 60)
        print("\n💡 Próximo paso: Reiniciar servicios backend y celery")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("⚠️  Migración falló - revisar errores")
        print("=" * 60)
        sys.exit(1)



