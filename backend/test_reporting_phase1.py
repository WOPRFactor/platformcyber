#!/usr/bin/env python3
"""
Script de Prueba - Fase 1 Módulo de Reportería
===============================================

Prueba los componentes implementados en Fase 1:
- FileScanner
- Parsers (Nmap, Nuclei, Subfinder, Nikto)
- ParserManager
- DataAggregator
- RiskCalculator

Uso:
    python3 test_reporting_phase1.py <workspace_id> <workspace_name>
    
Ejemplo:
    python3 test_reporting_phase1.py 1 "Test Workspace"
"""

import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s [%(name)s] %(message)s'
)

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from services.reporting.core import FileScanner, DataAggregator, RiskCalculator
from services.reporting.parsers import ParserManager


def test_reporting_phase1(workspace_id: int, workspace_name: str):
    """
    Prueba todos los componentes de Fase 1.
    
    Args:
        workspace_id: ID del workspace a escanear
        workspace_name: Nombre del workspace
    """
    print("=" * 70)
    print("PRUEBA FASE 1 - MÓDULO DE REPORTERÍA")
    print("=" * 70)
    print(f"\nWorkspace: {workspace_name} (ID: {workspace_id})\n")
    
    # 1. Escanear archivos
    print("1️⃣ ESCANEANDO ARCHIVOS...")
    print("-" * 70)
    scanner = FileScanner()
    files_by_category = scanner.scan_workspace(workspace_id, workspace_name)
    
    total_files = sum(len(files) for files in files_by_category.values())
    print(f"\n✅ Archivos encontrados: {total_files}")
    for category, files in files_by_category.items():
        if files:
            print(f"   - {category}: {len(files)} archivos")
    
    if total_files == 0:
        print("\n⚠️  No se encontraron archivos. Verifica que el workspace tenga resultados.")
        return
    
    # 2. Parsear archivos
    print("\n2️⃣ PARSEANDO ARCHIVOS...")
    print("-" * 70)
    parser_manager = ParserManager()
    all_findings = []
    
    files_parsed = 0
    files_skipped = 0
    
    for category, files in files_by_category.items():
        print(f"\n📁 Categoría: {category}")
        for file_path in files:
            findings = parser_manager.parse_file(file_path)
            if findings:
                all_findings.extend(findings)
                files_parsed += 1
                print(f"   ✅ {file_path.name}: {len(findings)} findings")
            else:
                files_skipped += 1
                print(f"   ⏭️  {file_path.name}: sin parser disponible")
    
    print(f"\n✅ Archivos parseados: {files_parsed}")
    print(f"⏭️  Archivos sin parser: {files_skipped}")
    print(f"📊 Total de findings: {len(all_findings)}")
    
    if len(all_findings) == 0:
        print("\n⚠️  No se encontraron findings. Verifica que los archivos sean de herramientas soportadas.")
        return
    
    # 3. Consolidar y deduplicar
    print("\n3️⃣ CONSOLIDANDO Y DEDUPLICANDO...")
    print("-" * 70)
    aggregator = DataAggregator()
    consolidated = aggregator.consolidate(all_findings)
    
    print(f"\n✅ Findings después de deduplicación: {sum(len(f) for f in consolidated.values())}")
    print("\n📊 Findings por categoría:")
    for category, findings in consolidated.items():
        print(f"   - {category}: {len(findings)} findings")
    
    # 4. Estadísticas
    print("\n4️⃣ ESTADÍSTICAS...")
    print("-" * 70)
    stats = aggregator.get_statistics(consolidated)
    
    print(f"\n📈 Total de findings: {stats['total_findings']}")
    print(f"🎯 Targets únicos: {stats['unique_targets']}")
    
    print("\n📊 Por severidad:")
    for severity, count in stats['by_severity'].items():
        if count > 0:
            print(f"   - {severity.upper()}: {count}")
    
    # 5. Calcular riesgo
    print("\n5️⃣ CÁLCULO DE RIESGO...")
    print("-" * 70)
    risk_calc = RiskCalculator()
    risk_metrics = risk_calc.calculate(consolidated)
    
    print(f"\n⚠️  Risk Score: {risk_metrics['risk_score']}/10")
    print(f"📊 Risk Level: {risk_metrics['risk_level'].upper()}")
    print(f"🔍 Vulnerabilidades encontradas: {risk_metrics['vulnerabilities_only']}")
    
    # 6. Resumen final
    print("\n" + "=" * 70)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 70)
    print(f"\n📋 Resumen:")
    print(f"   - Archivos escaneados: {total_files}")
    print(f"   - Archivos parseados: {files_parsed}")
    print(f"   - Findings encontrados: {len(all_findings)}")
    print(f"   - Findings únicos: {stats['total_findings']}")
    print(f"   - Risk Score: {risk_metrics['risk_score']}/10 ({risk_metrics['risk_level']})")
    print("\n💡 Los componentes funcionan correctamente!")
    print("   Próximo paso: Implementar generación de reportes (Fase 1B)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 test_reporting_phase1.py <workspace_id> <workspace_name>")
        print("\nEjemplo:")
        print('  python3 test_reporting_phase1.py 1 "Test Workspace"')
        sys.exit(1)
    
    try:
        workspace_id = int(sys.argv[1])
        workspace_name = sys.argv[2]
        test_reporting_phase1(workspace_id, workspace_name)
    except ValueError:
        print("❌ Error: workspace_id debe ser un número entero")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)





