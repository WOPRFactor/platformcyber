#!/bin/bash

################################################################################
# Script de Detención - Cybersecurity Platform
# ============================================
#
# Este script detiene todos los servicios de desarrollo:
#   - Frontend (Vite/React) en puerto 5179
#   - Backend (Flask) en puerto 5000
#   - Celery Worker
#   - Redis en puerto 6379 (opcional)
#
# Uso:
#   ./stop-dev.sh          # Detener servicios (mantiene Redis)
#   ./stop-dev.sh --all     # Detener todos incluyendo Redis
#   ./stop-dev.sh --force   # Forzar detención inmediata
#
# Autor: Factor X
# Fecha: Diciembre 2025
# Versión: 1.0.0
################################################################################

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
PLATFORM_DIR="$PROJECT_DIR/platform"
BACKEND_DIR="$PLATFORM_DIR/backend"
FRONTEND_DIR="$PLATFORM_DIR/frontend"
LOG_DIR="$PROJECT_DIR/logs"
PID_DIR="$PROJECT_DIR/.pids"

# Puertos
BACKEND_PORT=5000
FRONTEND_PORT=5179
REDIS_PORT=6379

# Opciones
STOP_REDIS=false
FORCE_STOP=false

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_header() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Verificar que un proceso está corriendo
process_running() {
    local pid=$1
    [[ -n "$pid" ]] && ps -p "$pid" >/dev/null 2>&1
}

# Verificar si un puerto está en uso
port_in_use() {
    local port=$1
    if command -v lsof >/dev/null 2>&1; then
        lsof -i ":$port" >/dev/null 2>&1
    elif command -v netstat >/dev/null 2>&1; then
        netstat -tuln 2>/dev/null | grep -q ":$port "
    else
        return 1
    fi
}

# Obtener PID de un proceso en un puerto
get_pid_on_port() {
    local port=$1
    if command -v lsof >/dev/null 2>&1; then
        lsof -ti ":$port" 2>/dev/null | head -1
    elif command -v netstat >/dev/null 2>&1; then
        netstat -tulnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1 | head -1
    else
        return 1
    fi
}

# Leer PID desde archivo
read_pid() {
    local service=$1
    local pid_file="$PID_DIR/${service}.pid"
    if [[ -f "$pid_file" ]]; then
        cat "$pid_file" 2>/dev/null | tr -d '\n' || echo ""
    else
        echo ""
    fi
}

# Verificar que un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ==============================================================================
# FUNCIONES DE DETENCIÓN
# ==============================================================================

stop_frontend() {
    local pid=$(read_pid "frontend")
    
    if [[ -z "$pid" ]] || ! process_running "$pid"; then
        # Intentar encontrar por puerto o proceso
        if port_in_use "$FRONTEND_PORT"; then
            pid=$(get_pid_on_port "$FRONTEND_PORT")
        else
            # Buscar por proceso vite
            pid=$(pgrep -f "vite.*$FRONTEND_PORT" 2>/dev/null | head -1 || echo "")
            if [[ -z "$pid" ]]; then
                pid=$(pgrep -f "node.*vite" 2>/dev/null | head -1 || echo "")
            fi
        fi
    fi
    
    if [[ -z "$pid" ]]; then
        print_warning "Frontend no está corriendo"
        rm -f "$PID_DIR/frontend.pid"
        return 0
    fi
    
    if process_running "$pid"; then
        print_info "Deteniendo Frontend (PID: $pid)..."
        
        if [[ "$FORCE_STOP" == true ]]; then
            # Forzar detención inmediata
            pkill -9 -P "$pid" 2>/dev/null || true
            kill -9 "$pid" 2>/dev/null || true
        else
            # Detención suave
            pkill -P "$pid" 2>/dev/null || true
            kill "$pid" 2>/dev/null || true
            sleep 2
            
            # Si aún está corriendo, forzar
            if process_running "$pid"; then
                print_warning "Forzando detención del Frontend..."
                pkill -9 -P "$pid" 2>/dev/null || true
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi
        
        sleep 1
        
        if process_running "$pid"; then
            print_error "No se pudo detener el Frontend completamente"
            return 1
        else
            print_success "Frontend detenido"
            rm -f "$PID_DIR/frontend.pid"
        fi
    fi
}

stop_backend() {
    local pid=$(read_pid "backend")
    
    if [[ -z "$pid" ]] || ! process_running "$pid"; then
        # Intentar encontrar por puerto
        if port_in_use "$BACKEND_PORT"; then
            pid=$(get_pid_on_port "$BACKEND_PORT")
        else
            # Buscar por proceso flask/python app.py
            pid=$(pgrep -f "python.*app.py" 2>/dev/null | head -1 || echo "")
            if [[ -z "$pid" ]]; then
                pid=$(pgrep -f "flask.*run" 2>/dev/null | head -1 || echo "")
            fi
        fi
    fi
    
    if [[ -z "$pid" ]]; then
        print_warning "Backend no está corriendo"
        rm -f "$PID_DIR/backend.pid"
        return 0
    fi
    
    if process_running "$pid"; then
        print_info "Deteniendo Backend (PID: $pid)..."
        
        if [[ "$FORCE_STOP" == true ]]; then
            # Forzar detención inmediata
            kill -9 "$pid" 2>/dev/null || true
        else
            # Detención suave
            kill "$pid" 2>/dev/null || true
            sleep 2
            
            # Si aún está corriendo, forzar
            if process_running "$pid"; then
                print_warning "Forzando detención del Backend..."
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi
        
        sleep 1
        
        if process_running "$pid"; then
            print_error "No se pudo detener el Backend completamente"
            return 1
        else
            print_success "Backend detenido"
            rm -f "$PID_DIR/backend.pid"
        fi
    fi
}

stop_celery() {
    local pid=$(read_pid "celery")
    
    if [[ -z "$pid" ]] || ! process_running "$pid"; then
        # Buscar por proceso celery
        pid=$(pgrep -f "celery.*worker" 2>/dev/null | head -1 || echo "")
    fi
    
    if [[ -z "$pid" ]]; then
        print_warning "Celery no está corriendo"
        rm -f "$PID_DIR/celery.pid"
        return 0
    fi
    
    if process_running "$pid"; then
        print_info "Deteniendo Celery (PID: $pid)..."
        
        if [[ "$FORCE_STOP" == true ]]; then
            # Forzar detención inmediata
            pkill -9 -P "$pid" 2>/dev/null || true
            kill -9 "$pid" 2>/dev/null || true
        else
            # Detención suave
            pkill -P "$pid" 2>/dev/null || true
            kill "$pid" 2>/dev/null || true
            sleep 2
            
            # Si aún está corriendo, forzar
            if process_running "$pid"; then
                print_warning "Forzando detención de Celery..."
                pkill -9 -P "$pid" 2>/dev/null || true
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi
        
        sleep 1
        
        if process_running "$pid"; then
            print_error "No se pudo detener Celery completamente"
            return 1
        else
            print_success "Celery detenido"
            rm -f "$PID_DIR/celery.pid"
        fi
    fi
}

stop_redis() {
    local pid=$(read_pid "redis")
    
    if [[ -z "$pid" ]] || ! process_running "$pid"; then
        # Intentar encontrar por puerto
        if port_in_use "$REDIS_PORT"; then
            pid=$(get_pid_on_port "$REDIS_PORT")
        else
            # Buscar por proceso redis-server
            pid=$(pgrep -f "redis-server" 2>/dev/null | head -1 || echo "")
        fi
    fi
    
    if [[ -z "$pid" ]]; then
        print_warning "Redis no está corriendo"
        rm -f "$PID_DIR/redis.pid"
        return 0
    fi
    
    if process_running "$pid"; then
        print_info "Deteniendo Redis (PID: $pid)..."
        
        # Usar redis-cli shutdown si está disponible (más seguro)
        if command_exists redis-cli && [[ "$FORCE_STOP" != true ]]; then
            redis-cli shutdown 2>/dev/null || kill "$pid" 2>/dev/null || true
            sleep 2
        else
            if [[ "$FORCE_STOP" == true ]]; then
                kill -9 "$pid" 2>/dev/null || true
            else
                kill "$pid" 2>/dev/null || true
                sleep 2
            fi
        fi
        
        # Si aún está corriendo, forzar
        if process_running "$pid"; then
            print_warning "Forzando detención de Redis..."
            kill -9 "$pid" 2>/dev/null || true
        fi
        
        sleep 1
        
        if process_running "$pid"; then
            print_error "No se pudo detener Redis completamente"
            return 1
        else
            print_success "Redis detenido"
            rm -f "$PID_DIR/redis.pid"
        fi
    fi
}

# ==============================================================================
# FUNCIÓN PRINCIPAL
# ==============================================================================

stop_all_services() {
    print_header "🛑 DETENIENDO SERVICIOS DE DESARROLLO"
    
    # Crear directorio de PIDs si no existe
    mkdir -p "$PID_DIR" 2>/dev/null || true
    
    # Detener servicios en orden inverso al inicio
    stop_frontend
    echo ""
    
    stop_backend
    echo ""
    
    stop_celery
    echo ""
    
    # Detener Redis solo si se solicita
    if [[ "$STOP_REDIS" == true ]]; then
        stop_redis
        echo ""
    else
        print_info "Redis se mantiene corriendo (usa --all para detenerlo también)"
    fi
    
    echo ""
    print_header "✅ SERVICIOS DETENIDOS"
    
    # Mostrar resumen
    echo -e "${GREEN}Servicios detenidos:${NC}"
    echo -e "   ${CYAN}✓${NC} Frontend (puerto $FRONTEND_PORT)"
    echo -e "   ${CYAN}✓${NC} Backend (puerto $BACKEND_PORT)"
    echo -e "   ${CYAN}✓${NC} Celery Worker"
    if [[ "$STOP_REDIS" == true ]]; then
        echo -e "   ${CYAN}✓${NC} Redis (puerto $REDIS_PORT)"
    else
        echo -e "   ${YELLOW}○${NC} Redis (mantenido corriendo)"
    fi
    
    echo ""
    print_info "Para iniciar los servicios nuevamente, ejecuta: ./start-dev.sh"
}

# ==============================================================================
# PROCESAR ARGUMENTOS
# ==============================================================================

show_help() {
    echo "Uso: $0 [OPCIONES]"
    echo ""
    echo "Detiene todos los servicios de desarrollo."
    echo ""
    echo "Opciones:"
    echo "  --all      Detener todos los servicios incluyendo Redis"
    echo "  --force    Forzar detención inmediata (sin esperar cierre suave)"
    echo "  -h, --help Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0              # Detener servicios (mantiene Redis)"
    echo "  $0 --all        # Detener todos incluyendo Redis"
    echo "  $0 --force      # Forzar detención inmediata"
    echo "  $0 --all --force # Detener todo forzadamente"
}

# Procesar argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            STOP_REDIS=true
            shift
            ;;
        --force)
            FORCE_STOP=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Opción desconocida: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
done

# ==============================================================================
# EJECUTAR
# ==============================================================================

stop_all_services


