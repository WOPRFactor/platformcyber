#!/bin/bash

# Script para aplicar el fix de separación de workspaces
# Autor: Claude
# Fecha: 23/Nov/2025

echo "🔧 Aplicando fix de separación de workspaces..."
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para backup
backup_file() {
    local file=$1
    if [ -f "$file" ]; then
        cp "$file" "${file}.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${GREEN}✓${NC} Backup creado: ${file}.backup"
    fi
}

# Verificar que estamos en el directorio correcto
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Error: Este script debe ejecutarse desde la raíz del proyecto${NC}"
    echo "   (debe contener las carpetas 'backend' y 'frontend')"
    exit 1
fi

echo "📁 Directorio del proyecto detectado correctamente"
echo ""

# Backend changes
echo -e "${BLUE}[1/5]${NC} Actualizando backend/api/v1/scanning.py..."
backup_file "backend/api/v1/scanning.py"
cp scanning.py.NEW backend/api/v1/scanning.py
echo -e "${GREEN}✓${NC} Backend actualizado"
echo ""

# Frontend API
echo -e "${BLUE}[2/5]${NC} Actualizando frontend/src/lib/api/scanning/scanning.ts..."
backup_file "frontend/src/lib/api/scanning/scanning.ts"
cp scanning.ts.NEW frontend/src/lib/api/scanning/scanning.ts
echo -e "${GREEN}✓${NC} API de scanning actualizada"
echo ""

# Dashboard
echo -e "${BLUE}[3/5]${NC} Actualizando frontend/src/pages/Dashboard.tsx..."
backup_file "frontend/src/pages/Dashboard.tsx"
cp Dashboard.tsx.NEW frontend/src/pages/Dashboard.tsx
echo -e "${GREEN}✓${NC} Dashboard actualizado"
echo ""

# Scanning page
echo -e "${BLUE}[4/5]${NC} Actualizando frontend/src/pages/Scanning.tsx..."
backup_file "frontend/src/pages/Scanning.tsx"
cp Scanning.tsx.NEW frontend/src/pages/Scanning.tsx
echo -e "${GREEN}✓${NC} Página de Scanning actualizada"
echo ""

# DashboardEnhanced
echo -e "${BLUE}[5/5]${NC} Actualizando frontend/src/pages/DashboardEnhanced.tsx..."
backup_file "frontend/src/pages/DashboardEnhanced.tsx"
cp DashboardEnhanced.tsx.NEW frontend/src/pages/DashboardEnhanced.tsx
echo -e "${GREEN}✓${NC} DashboardEnhanced actualizado"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Fix aplicado exitosamente${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Próximos pasos:"
echo ""
echo "1. Backend:"
echo "   cd backend"
echo "   # Reiniciar el servidor Flask"
echo ""
echo "2. Frontend:"
echo "   cd frontend"
echo "   npm run dev  # o el comando que uses"
echo ""
echo "3. Testing:"
echo "   - Selecciona un workspace en la UI"
echo "   - Crea algunos scans"
echo "   - Cambia a otro workspace"
echo "   - Verifica que los scans NO se mezclan"
echo ""
echo "📄 Documentación completa: WORKSPACE_SEPARATION_FIX.md"
echo ""
echo "💾 Backups creados con timestamp en cada archivo modificado"
echo ""
