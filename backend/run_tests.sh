#!/bin/bash

###############################################################################
# Script para ejecutar tests con diferentes opciones
###############################################################################

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                  ║${NC}"
echo -e "${GREEN}║       🧪 PENTESTING PLATFORM - TEST RUNNER      ║${NC}"
echo -e "${GREEN}║                                                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: Ejecutar desde el directorio backend/${NC}"
    exit 1
fi

# Activar virtual environment si existe
if [ -d "venv" ]; then
    echo -e "${YELLOW}🔧 Activando virtual environment...${NC}"
    source venv/bin/activate
fi

# Función para ejecutar tests
run_tests() {
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    eval $2
    echo ""
}

# Opción por defecto
TEST_TYPE=${1:-all}

case $TEST_TYPE in
    
    # Todos los tests con coverage
    all)
        run_tests "📊 Ejecutando TODOS los tests con coverage" \
            "pytest tests/ -v --cov=. --cov-report=html --cov-report=term"
        ;;
    
    # Tests rápidos (sin coverage)
    quick)
        run_tests "⚡ Ejecutando tests rápidos (sin coverage)" \
            "pytest tests/ -v"
        ;;
    
    # Solo tests de servicios
    services)
        run_tests "🔧 Ejecutando tests de SERVICIOS" \
            "pytest tests/test_services.py -v"
        ;;
    
    # Solo tests de endpoints
    endpoints)
        run_tests "🌐 Ejecutando tests de ENDPOINTS" \
            "pytest tests/test_endpoints.py -v"
        ;;
    
    # Solo tests de parsers
    parsers)
        run_tests "📝 Ejecutando tests de PARSERS" \
            "pytest tests/test_parsers.py -v"
        ;;
    
    # Solo tests de integración
    integration)
        run_tests "🔗 Ejecutando tests de INTEGRACIÓN" \
            "pytest tests/test_integration.py -v"
        ;;
    
    # Tests con markers específicos
    unit)
        run_tests "🧩 Ejecutando UNIT TESTS" \
            "pytest tests/ -v -m unit"
        ;;
    
    # Tests lentos
    slow)
        run_tests "🐌 Ejecutando tests LENTOS" \
            "pytest tests/ -v -m slow"
        ;;
    
    # Tests con output detallado
    verbose)
        run_tests "📢 Ejecutando tests con output VERBOSE" \
            "pytest tests/ -vv -s"
        ;;
    
    # Tests con coverage y reporte HTML
    coverage)
        run_tests "📊 Ejecutando tests con COVERAGE completo" \
            "pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing"
        echo -e "${GREEN}✅ Reporte HTML generado en: htmlcov/index.html${NC}"
        ;;
    
    # Tests en modo watch (requiere pytest-watch)
    watch)
        run_tests "👀 Ejecutando tests en modo WATCH" \
            "ptw tests/ -- -v"
        ;;
    
    # Linting (flake8)
    lint)
        run_tests "🔍 Ejecutando LINTING (flake8)" \
            "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"
        ;;
    
    # Security scan (bandit)
    security)
        run_tests "🔒 Ejecutando SECURITY SCAN (bandit)" \
            "bandit -r . -ll"
        ;;
    
    # Dependency check (safety)
    deps)
        run_tests "📦 Verificando DEPENDENCIAS (safety)" \
            "safety check"
        ;;
    
    # Full check (tests + lint + security)
    check)
        run_tests "🧪 Tests" \
            "pytest tests/ -v --cov=. --cov-report=term"
        run_tests "🔍 Linting" \
            "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"
        run_tests "🔒 Security" \
            "bandit -r . -ll"
        echo -e "${GREEN}✅ ¡Todas las verificaciones completadas!${NC}"
        ;;
    
    # Ayuda
    help|--help|-h)
        echo "Uso: ./run_tests.sh [OPCIÓN]"
        echo ""
        echo "Opciones disponibles:"
        echo "  all          - Ejecutar todos los tests con coverage (default)"
        echo "  quick        - Tests rápidos sin coverage"
        echo "  services     - Solo tests de servicios"
        echo "  endpoints    - Solo tests de endpoints"
        echo "  parsers      - Solo tests de parsers"
        echo "  integration  - Solo tests de integración"
        echo "  unit         - Solo unit tests (marker)"
        echo "  slow         - Solo tests lentos (marker)"
        echo "  verbose      - Tests con output detallado"
        echo "  coverage     - Tests con coverage completo + HTML"
        echo "  watch        - Tests en modo watch (requiere pytest-watch)"
        echo "  lint         - Solo linting (flake8)"
        echo "  security     - Solo security scan (bandit)"
        echo "  deps         - Verificar dependencias (safety)"
        echo "  check        - Tests + Lint + Security"
        echo "  help         - Mostrar esta ayuda"
        echo ""
        echo "Ejemplos:"
        echo "  ./run_tests.sh                # Ejecutar todos los tests"
        echo "  ./run_tests.sh quick          # Tests rápidos"
        echo "  ./run_tests.sh coverage       # Coverage completo"
        echo "  ./run_tests.sh check          # Verificación completa"
        exit 0
        ;;
    
    *)
        echo -e "${RED}❌ Opción desconocida: $TEST_TYPE${NC}"
        echo "Usar './run_tests.sh help' para ver opciones disponibles"
        exit 1
        ;;
esac

echo -e "${GREEN}✅ ¡Ejecución completada!${NC}"



