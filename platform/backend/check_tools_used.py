#!/usr/bin/env python3
"""
Script para verificar tools_used en reportes generados.

Uso:
    python3 check_tools_used.py [--last N] [--all]
"""

import sys
from app import create_app
from models.report import Report

def main():
    app = create_app()
    
    with app.app_context():
        # Verificar argumentos
        show_all = '--all' in sys.argv
        last_n = 1
        if '--last' in sys.argv:
            try:
                idx = sys.argv.index('--last')
                last_n = int(sys.argv[idx + 1])
            except (IndexError, ValueError):
                pass
        
        if show_all:
            reports = Report.query.order_by(Report.created_at.desc()).limit(20).all()
        else:
            reports = Report.query.order_by(Report.created_at.desc()).limit(last_n).all()
        
        if not reports:
            print("❌ No hay reportes en la base de datos")
            return
        
        print("=" * 70)
        print("REPORTES GENERADOS - VERIFICACIÓN DE tools_used")
        print("=" * 70)
        
        for i, report in enumerate(reports, 1):
            print(f"\n📄 REPORTE #{i} (ID: {report.id})")
            print("-" * 70)
            print(f"Título: {report.title}")
            print(f"Workspace ID: {report.workspace_id}")
            print(f"Tipo: {report.report_type} | Formato: {report.format}")
            print(f"Fecha: {report.created_at}")
            
            print(f"\n📊 METADATA:")
            print(f"  Files Processed: {report.files_processed}")
            print(f"  Total Findings: {report.total_findings}")
            print(f"  Risk Score: {report.risk_score:.2f}")
            print(f"  Severidad: Critical={report.critical_count}, High={report.high_count}, "
                  f"Medium={report.medium_count}, Low={report.low_count}, Info={report.info_count}")
            
            print(f"\n🔧 TOOLS USED:")
            if report.tools_used:
                print(f"  ✅ {len(report.tools_used)} herramienta(s) detectada(s):")
                for tool in sorted(report.tools_used):
                    print(f"     • {tool}")
            else:
                print(f"  ⚠️  Ninguna herramienta detectada (vacío o None)")
            
            if report.file_path:
                from pathlib import Path
                file_path = Path(report.file_path)
                exists = "✅" if file_path.exists() else "❌"
                print(f"\n📁 Archivo PDF: {exists} {report.file_path}")
                if file_path.exists():
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    print(f"   Tamaño: {size_mb:.2f} MB")
        
        # Estadísticas generales
        print("\n" + "=" * 70)
        print("📈 ESTADÍSTICAS GENERALES")
        print("=" * 70)
        
        total_reports = Report.query.count()
        reports_with_tools = Report.query.filter(
            Report.tools_used.isnot(None)
        ).filter(
            Report.tools_used != []
        ).count()
        reports_empty = total_reports - reports_with_tools
        
        print(f"Total reportes: {total_reports}")
        print(f"Con tools_used: {reports_with_tools} ({reports_with_tools*100/total_reports if total_reports > 0 else 0:.1f}%)")
        print(f"Sin tools_used: {reports_empty} ({reports_empty*100/total_reports if total_reports > 0 else 0:.1f}%)")
        
        # Herramientas más usadas
        from collections import Counter
        all_tools = []
        for r in Report.query.filter(Report.tools_used.isnot(None)).all():
            if r.tools_used:
                all_tools.extend(r.tools_used)
        
        if all_tools:
            tool_counts = Counter(all_tools)
            print(f"\n🔝 HERRAMIENTAS MÁS USADAS:")
            for tool, count in tool_counts.most_common(10):
                print(f"  {tool:20} → {count:3} reporte(s)")

if __name__ == '__main__':
    main()

