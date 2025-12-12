#!/bin/bash
# Script para habilitar Corepack y arreglar npm
# Ejecutar con: bash scripts/enable_corepack.sh

echo "=== Habilitando Corepack ==="
sudo corepack enable

echo ""
echo "Verificando npm..."
npm --version

echo ""
echo "✅ Corepack habilitado. npm debería funcionar ahora."
