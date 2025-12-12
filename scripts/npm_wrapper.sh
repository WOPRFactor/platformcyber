#!/bin/bash
# Wrapper para npm que funciona sin corepack habilitado
# Usa el npm del cache de corepack

NPM_BIN="/home/kali/.cache/node/corepack/npm/11.6.4/bin/npm"

if [ ! -f "$NPM_BIN" ]; then
    echo "Error: npm no encontrado en $NPM_BIN"
    exit 1
fi

# Ejecutar npm con los argumentos pasados
exec "$NPM_BIN" "$@"
