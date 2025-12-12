#!/bin/bash

################################################################################
# Script de Inicio Unificado - Cybersecurity Platform
# ====================================================
#
# Este script inicia de forma confiable los servicios de desarrollo:
#   - Backend (Flask) en puerto 5001
#   - Frontend (Vite/React) en puerto 5180
#
# Uso:
#   ./start-dev.sh          # Iniciar servicios
#   ./start-dev.sh stop     # Detener servicios
#   ./start-dev.sh status   # Ver estado
#   ./start-dev.sh logs     # Ver logs
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
BACKEND_PORT=5001  # Puerto separado para dev4-improvements
FRONTEND_PORT=5180  # Puerto separado para dev4-improvements
REDIS_PORT=6379

# URLs
BACKEND_URL="http://localhost:${BACKEND_PORT}"
FRONTEND_URL="http://localhost:${FRONTEND_PORT}"
BACKEND_API_URL="${BACKEND_URL}/api/v1"

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

# Verificar que un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Encontrar npm (puede estar en alias o en PATH)
find_npm() {
    # Primero intentar ejecutar npm directamente (funciona con alias de zsh)
    if command_exists npm; then
        # En zsh, los alias funcionan directamente, así que usar npm
        echo "npm"
        return 0
    fi
    
    # Buscar en ubicaciones comunes
    local common_paths=(
        "/usr/bin/npm"
        "/usr/local/bin/npm"
    )
    
    for path in "${common_paths[@]}"; do
        if [[ -f "$path" ]] && [[ -x "$path" ]]; then
            echo "$path"
            return 0
        fi
    done
    
    # Buscar con glob patterns
    local glob_paths=(
        "$HOME/.nvm/versions/node/*/bin/npm"
        "$HOME/.cache/node/corepack/npm/*/bin/npm"
    )
    
    for pattern in "${glob_paths[@]}"; do
        local found=$(ls -1 $pattern 2>/dev/null | head -1)
        if [[ -n "$found" ]] && [[ -x "$found" ]]; then
            echo "$found"
            return 0
        fi
    done
    
    return 1
}

# Verificar si un puerto está en uso
port_in_use() {
    local port=$1
    # Intentar primero con netstat/ss (más confiable para procesos de root)
    if command_exists netstat; then
        netstat -tlnp 2>/dev/null | grep -q ":$port " && return 0
    fi
    if command_exists ss; then
        ss -tlnp 2>/dev/null | grep -q ":$port " && return 0
    fi
    # Fallback a lsof (puede fallar si el proceso es de otro usuario)
    if command_exists lsof; then
        lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1 && return 0
    fi
    # Último fallback: intentar conexión
    timeout 1 bash -c "echo > /dev/tcp/localhost/$port" 2>/dev/null
}

# Obtener PID de un proceso en un puerto
get_pid_on_port() {
    local port=$1
    # Intentar primero con netstat/ss (más confiable para procesos de root)
    if command_exists netstat; then
        local pid=$(netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1 | head -1)
        [[ -n "$pid" ]] && echo "$pid" && return 0
    fi
    if command_exists ss; then
        local pid=$(ss -tlnp 2>/dev/null | grep ":$port " | grep -oP 'pid=\K[0-9]+' | head -1)
        [[ -n "$pid" ]] && echo "$pid" && return 0
    fi
    # Fallback a lsof (puede fallar si el proceso es de otro usuario)
    if command_exists lsof; then
        lsof -ti :"$port" 2>/dev/null | head -1
    fi
}

# Verificar que un proceso está corriendo
process_running() {
    local pid=$1
    kill -0 "$pid" 2>/dev/null
}

# Crear directorios necesarios
setup_directories() {
    mkdir -p "$LOG_DIR"
    mkdir -p "$PID_DIR"
}

# Guardar PID
save_pid() {
    local service=$1
    local pid=$2
    echo "$pid" > "$PID_DIR/${service}.pid"
}

# Leer PID guardado
read_pid() {
    local service=$1
    if [[ -f "$PID_DIR/${service}.pid" ]]; then
        cat "$PID_DIR/${service}.pid"
    fi
}

# Verificar dependencias
check_dependencies() {
    print_info "Verificando dependencias..."
    
    local missing=()
    
    # Python3
    if ! command_exists python3; then
        missing+=("python3")
    else
        print_success "Python3 encontrado: $(python3 --version)"
    fi
    
    # npm (opcional - se puede usar Vite directamente)
    if ! NPM_PATH=$(find_npm); then
        print_warning "npm no encontrado"
        print_info "Se usará Vite directamente como fallback"
        export NPM_CMD=""
    else
        # Si es solo "npm", verificar que funciona correctamente
        if [[ "$NPM_PATH" == "npm" ]]; then
            # Probar ejecutar npm --version con timeout para evitar bloqueos
            if ! timeout 2 npm --version >/dev/null 2>&1; then
                print_warning "npm encontrado pero no funciona correctamente (problema conocido con Corepack)"
                print_info "Se usará Vite directamente como fallback"
                export NPM_CMD=""
            else
                print_success "npm encontrado: $(which npm 2>/dev/null || echo 'npm (alias)')"
                export NPM_CMD="npm"
            fi
        else
            # Verificar que el npm encontrado funciona
            if ! timeout 2 "$NPM_PATH" --version >/dev/null 2>&1; then
                print_warning "npm en $NPM_PATH no funciona correctamente"
                print_info "Se usará Vite directamente como fallback"
                export NPM_CMD=""
            else
                print_success "npm encontrado: $NPM_PATH"
                export NPM_CMD="$NPM_PATH"
            fi
        fi
    fi
    
    # Verificar directorios
    if [[ ! -d "$BACKEND_DIR" ]]; then
        print_error "Directorio backend no encontrado: $BACKEND_DIR"
        exit 1
    fi
    
    if [[ ! -d "$FRONTEND_DIR" ]]; then
        print_error "Directorio frontend no encontrado: $FRONTEND_DIR"
        exit 1
    fi
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        print_error "Dependencias faltantes: ${missing[*]}"
        exit 1
    fi
    
    # Verificar node_modules (solo si npm está disponible)
    if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
        if [[ -n "${NPM_CMD:-}" ]]; then
            print_warning "node_modules no encontrado. Ejecutando npm install..."
            cd "$FRONTEND_DIR"
            "$NPM_CMD" install
        else
            print_warning "node_modules no encontrado y npm no está disponible"
            print_error "Instala node_modules manualmente o instala npm"
            print_info "Puedes ejecutar: cd frontend && npm install"
            exit 1
        fi
    fi
}

# ==============================================================================
# FUNCIONES DE SERVICIOS
# ==============================================================================

start_backend() {
    print_info "Iniciando Backend (Flask) en puerto $BACKEND_PORT..."
    
    # Verificar si ya está corriendo
    if port_in_use "$BACKEND_PORT"; then
        local existing_pid=$(get_pid_on_port "$BACKEND_PORT")
        if [[ -n "$existing_pid" ]] && process_running "$existing_pid"; then
            print_warning "Backend ya está corriendo (PID: $existing_pid)"
            save_pid "backend" "$existing_pid"
            return 0
        fi
    fi
    
    # Cambiar al directorio del backend
    cd "$BACKEND_DIR"
    
    # Verificar que app.py existe
    if [[ ! -f "app.py" ]]; then
        print_error "app.py no encontrado en $BACKEND_DIR"
        return 1
    fi
    
    # Iniciar backend en background
    # NOTA: El sistema de logging de Python maneja los logs con rotación
    # en platform/backend/logs/app.log. Solo redirigimos stderr a un archivo
    # temporal para capturar errores de inicio, pero el logging real va a app.log
    # Usar Python del venv si existe
    local python_cmd="python3"
    if [[ -f "$BACKEND_DIR/venv/bin/python" ]]; then
        python_cmd="$BACKEND_DIR/venv/bin/python"
        print_info "Usando Python del venv: $python_cmd"
    fi
    
    print_info "Ejecutando: $python_cmd app.py"
    cd "$BACKEND_DIR"
    nohup $python_cmd app.py > "$LOG_DIR/backend_startup.log" 2>&1 &
    local backend_pid=$!
    
    # Guardar PID
    save_pid "backend" "$backend_pid"
    
    # Esperar y verificar
    print_info "Esperando que el backend inicie..."
    local max_attempts=15
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        sleep 2
        if port_in_use "$BACKEND_PORT"; then
            # Verificar que responde
            if curl -s "$BACKEND_URL/api/v1/system/health" >/dev/null 2>&1; then
                print_success "Backend iniciado correctamente (PID: $backend_pid)"
                print_info "  URL: $BACKEND_URL"
                print_info "  API: $BACKEND_API_URL"
                print_info "  Logs: $BACKEND_DIR/logs/app.log (con rotación automática)"
                # Limpiar archivo de startup después de 1 minuto (solo errores de inicio)
                (sleep 60 && rm -f "$LOG_DIR/backend_startup.log" 2>/dev/null) &
                return 0
            fi
        fi
        attempt=$((attempt + 1))
    done
    
    print_error "Backend no pudo iniciar correctamente"
    print_error "Ver logs de inicio en: $LOG_DIR/backend_startup.log"
    print_error "Ver logs de aplicación en: $BACKEND_DIR/logs/app.log"
    tail -20 "$LOG_DIR/backend_startup.log" 2>/dev/null || true
    return 1
}

start_redis() {
    print_info "Iniciando Redis en puerto $REDIS_PORT..."
    
    # Verificar si ya está corriendo
    if port_in_use "$REDIS_PORT"; then
        local existing_pid=$(get_pid_on_port "$REDIS_PORT")
        if [[ -n "$existing_pid" ]] && process_running "$existing_pid"; then
            print_warning "Redis ya está corriendo (PID: $existing_pid)"
            save_pid "redis" "$existing_pid"
            return 0
        fi
    fi
    
    # Verificar si redis-server está disponible
    if ! command_exists redis-server; then
        print_warning "redis-server no encontrado. Redis puede no estar instalado."
        print_info "Instala Redis con: sudo apt install redis-server"
        return 1
    fi
    
    # Iniciar Redis en background
    print_info "Ejecutando: redis-server --daemonize yes"
    redis-server --daemonize yes 2>/dev/null || true
    
    # Esperar y verificar
    sleep 2
    if port_in_use "$REDIS_PORT"; then
        local redis_pid=$(get_pid_on_port "$REDIS_PORT")
        if [[ -n "$redis_pid" ]]; then
            save_pid "redis" "$redis_pid"
            print_success "Redis iniciado correctamente (PID: $redis_pid)"
            print_info "  Puerto: $REDIS_PORT"
            return 0
        fi
    fi
    
    print_error "Redis no pudo iniciar correctamente"
    return 1
}

start_celery() {
    print_info "Iniciando Celery Worker..."
    
    # Verificar si ya está corriendo
    if pgrep -f "celery.*worker" >/dev/null 2>&1; then
        local existing_pid=$(pgrep -f "celery.*worker" | head -1)
        if [[ -n "$existing_pid" ]] && process_running "$existing_pid"; then
            print_warning "Celery ya está corriendo (PID: $existing_pid)"
            save_pid "celery" "$existing_pid"
            return 0
        fi
    fi
    
    # Cambiar al directorio del backend
    cd "$BACKEND_DIR"
    
    # Verificar que celery_app.py existe
    if [[ ! -f "celery_app.py" ]]; then
        print_warning "celery_app.py no encontrado. Celery puede no estar configurado."
        return 1
    fi
    
    # Verificar que Redis está corriendo (requisito de Celery)
    if ! port_in_use "$REDIS_PORT"; then
        print_warning "Redis no está corriendo. Iniciando Redis primero..."
        start_redis
        sleep 2
    fi
    
    # Verificar que existe el venv
    if [[ ! -f "$BACKEND_DIR/venv/bin/activate" ]]; then
        print_error "venv no encontrado en $BACKEND_DIR/venv"
        return 1
    fi
    
    # Iniciar Celery en background usando el Python del venv directamente
    # Usar nombre único para dev4 para evitar conflictos con dev3
    print_info "Iniciando Celery con venv de dev4 (nombre: celery_dev4@kali)..."
    cd "$BACKEND_DIR"
    
    # Usar el Python del venv directamente para garantizar que use las dependencias correctas
    nohup "$BACKEND_DIR/venv/bin/python" -m celery -A celery_app.celery worker \
        --hostname=celery_dev4@kali \
        --loglevel=info \
        --concurrency=2 \
        > "$LOG_DIR/celery.log" 2>&1 &
    local celery_pid=$!
    
    # Guardar PID
    save_pid "celery" "$celery_pid"
    
    # Esperar y verificar
    print_info "Esperando que Celery inicie..."
    sleep 5
    
    if process_running "$celery_pid"; then
        print_success "Celery Worker iniciado correctamente (PID: $celery_pid)"
        print_info "  Worker name: celery_dev4@kali"
        print_info "  Redis DB: 1 (dev4)"
        print_info "  Logs: $LOG_DIR/celery.log"
        return 0
    else
        print_error "Celery no pudo iniciar correctamente"
        print_error "Ver logs en: $LOG_DIR/celery.log"
        tail -20 "$LOG_DIR/celery.log" 2>/dev/null || true
        return 1
    fi
}

start_frontend() {
    print_info "Iniciando Frontend (Vite/React) en puerto $FRONTEND_PORT..."
    
    # Verificar si ya está corriendo
    if port_in_use "$FRONTEND_PORT"; then
        local existing_pid=$(get_pid_on_port "$FRONTEND_PORT")
        if [[ -n "$existing_pid" ]] && process_running "$existing_pid"; then
            print_warning "Frontend ya está corriendo (PID: $existing_pid)"
            save_pid "frontend" "$existing_pid"
            return 0
        fi
    fi
    
    # Cambiar al directorio del frontend
    cd "$FRONTEND_DIR"
    
    # Verificar que package.json existe
    if [[ ! -f "package.json" ]]; then
        print_error "package.json no encontrado en $FRONTEND_DIR"
        return 1
    fi
    
    # Iniciar frontend en background
    # Intentar usar npm, si falla usar Vite directamente
    cd "$FRONTEND_DIR"
    
    # Intentar usar npm si está disponible y funciona, sino usar Vite directamente
    if [[ -n "${NPM_CMD:-}" ]] && timeout 2 "$NPM_CMD" --version >/dev/null 2>&1; then
        print_info "Ejecutando: $NPM_CMD run dev"
        nohup bash -c "cd '$FRONTEND_DIR' && $NPM_CMD run dev" > "$LOG_DIR/frontend.log" 2>&1 &
        local frontend_pid=$!
    elif [[ -f "$FRONTEND_DIR/node_modules/.bin/vite" ]]; then
        print_info "Usando Vite directamente (npm no disponible o no funciona)"
        print_info "Ejecutando: node node_modules/.bin/vite"
        nohup bash -c "cd '$FRONTEND_DIR' && node node_modules/.bin/vite" > "$LOG_DIR/frontend.log" 2>&1 &
        local frontend_pid=$!
    else
        print_error "npm no funciona y Vite no encontrado en node_modules/.bin/"
        print_error "Ejecuta: cd frontend && npm install (o instala node_modules manualmente)"
        return 1
    fi
    
    # Guardar PID
    save_pid "frontend" "$frontend_pid"
    
    # Esperar y verificar
    print_info "Esperando que el frontend inicie (puede tardar 10-20 segundos)..."
    local max_attempts=20
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        sleep 2
        if port_in_use "$FRONTEND_PORT"; then
            # Verificar que responde
            if curl -s "$FRONTEND_URL" >/dev/null 2>&1; then
                print_success "Frontend iniciado correctamente (PID: $frontend_pid)"
                print_info "  URL: $FRONTEND_URL"
                print_info "  Logs: $LOG_DIR/frontend.log"
                return 0
            fi
        fi
        attempt=$((attempt + 1))
    done
    
    print_warning "Frontend puede estar aún compilando..."
    print_info "Ver logs en: $LOG_DIR/frontend.log"
    tail -20 "$LOG_DIR/frontend.log" 2>/dev/null || true
    return 0  # No fallar, puede estar compilando
}

stop_backend() {
    local pid=$(read_pid "backend")
    
    if [[ -z "$pid" ]] || ! process_running "$pid"; then
        # Intentar encontrar por puerto
        if port_in_use "$BACKEND_PORT"; then
            pid=$(get_pid_on_port "$BACKEND_PORT")
        else
            print_warning "Backend no está corriendo"
            return 0
        fi
    fi
    
    if [[ -n "$pid" ]] && process_running "$pid"; then
        print_info "Deteniendo Backend (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        sleep 2
        
        # Si aún está corriendo, forzar
        if process_running "$pid"; then
            kill -9 "$pid" 2>/dev/null || true
        fi
        
        print_success "Backend detenido"
        rm -f "$PID_DIR/backend.pid"
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
            pid=$(pgrep -f "redis-server" | head -1)
        fi
    fi
    
    if [[ -z "$pid" ]]; then
        print_warning "Redis no está corriendo"
        return 0
    fi
    
    if process_running "$pid"; then
        print_info "Deteniendo Redis (PID: $pid)..."
        # Usar redis-cli shutdown si está disponible (más seguro)
        if command_exists redis-cli; then
            redis-cli shutdown 2>/dev/null || kill "$pid" 2>/dev/null || true
        else
            kill "$pid" 2>/dev/null || true
        fi
        sleep 1
        
        # Si aún está corriendo, forzar
        if process_running "$pid"; then
            kill -9 "$pid" 2>/dev/null || true
        fi
        
        print_success "Redis detenido"
        rm -f "$PID_DIR/redis.pid"
    fi
}

stop_celery() {
    local pid=$(read_pid "celery")
    
    if [[ -z "$pid" ]] || ! process_running "$pid"; then
        # Buscar por proceso celery
        pid=$(pgrep -f "celery.*worker" | head -1)
    fi
    
    if [[ -z "$pid" ]]; then
        print_warning "Celery no está corriendo"
        return 0
    fi
    
    if process_running "$pid"; then
        print_info "Deteniendo Celery (PID: $pid)..."
        # Matar proceso y sus hijos
        pkill -P "$pid" 2>/dev/null || true
        kill "$pid" 2>/dev/null || true
        sleep 2
        
        # Si aún está corriendo, forzar
        if process_running "$pid"; then
            kill -9 "$pid" 2>/dev/null || true
        fi
        
        print_success "Celery detenido"
        rm -f "$PID_DIR/celery.pid"
    fi
}

stop_frontend() {
    local pid=$(read_pid "frontend")
    
    if [[ -z "$pid" ]] || ! process_running "$pid"; then
        # Intentar encontrar por puerto o proceso
        if port_in_use "$FRONTEND_PORT"; then
            pid=$(get_pid_on_port "$FRONTEND_PORT")
        else
            # Buscar por proceso vite
            pid=$(pgrep -f "vite.*$FRONTEND_PORT" | head -1)
        fi
    fi
    
    if [[ -z "$pid" ]]; then
        print_warning "Frontend no está corriendo"
        return 0
    fi
    
    if process_running "$pid"; then
        print_info "Deteniendo Frontend (PID: $pid)..."
        # Matar proceso y sus hijos
        pkill -P "$pid" 2>/dev/null || true
        kill "$pid" 2>/dev/null || true
        sleep 2
        
        # Si aún está corriendo, forzar
        if process_running "$pid"; then
            kill -9 "$pid" 2>/dev/null || true
        fi
        
        print_success "Frontend detenido"
        rm -f "$PID_DIR/frontend.pid"
    fi
}

# ==============================================================================
# FUNCIONES PRINCIPALES
# ==============================================================================

start_services() {
    print_header "🚀 INICIANDO SERVICIOS DE DESARROLLO"
    
    setup_directories
    check_dependencies
    
    # 1. Iniciar Redis primero (requisito para Celery y cache)
    if ! start_redis; then
        print_warning "Redis no pudo iniciar. Algunas funcionalidades pueden no estar disponibles."
    fi
    
    echo ""
    
    # 2. Iniciar Celery Worker
    if ! start_celery; then
        print_warning "Celery no pudo iniciar. Las tareas asíncronas no estarán disponibles."
    fi
    
    echo ""
    
    # 3. Iniciar backend
    if ! start_backend; then
        print_error "Error al iniciar backend. Abortando."
        exit 1
    fi
    
    echo ""
    
    # 4. Iniciar frontend
    if ! start_frontend; then
        print_warning "Frontend puede estar aún iniciando. Verifica los logs."
    fi
    
    echo ""
    print_header "✅ SERVICIOS INICIADOS"
    
    echo -e "${GREEN}📍 URLs de acceso:${NC}"
    echo -e "   ${CYAN}Frontend:${NC} $FRONTEND_URL"
    echo -e "   ${CYAN}Backend:${NC}  $BACKEND_URL"
    echo -e "   ${CYAN}API:${NC}      $BACKEND_API_URL"
    echo -e "   ${CYAN}Redis:${NC}    localhost:$REDIS_PORT"
    echo ""
    echo -e "${YELLOW}📝 Comandos útiles:${NC}"
    echo -e "   Ver estado:  ${BLUE}./start-dev.sh status${NC}"
    echo -e "   Ver logs:    ${BLUE}./start-dev.sh logs${NC}"
    echo -e "   Detener:     ${BLUE}./start-dev.sh stop${NC}"
    echo ""
}

stop_services() {
    print_header "🛑 DETENIENDO SERVICIOS"
    
    stop_frontend
    echo ""
    stop_backend
    echo ""
    stop_celery
    echo ""
    # Redis se deja corriendo por defecto (es un servicio del sistema)
    # Si quieres detenerlo también, descomenta la siguiente línea:
    # stop_redis
    
    echo ""
    print_success "Servicios detenidos"
    print_info "Nota: Redis se mantiene corriendo (servicio del sistema)"
}

show_status() {
    print_header "📊 ESTADO DE SERVICIOS"
    
    # Redis
    if port_in_use "$REDIS_PORT"; then
        local redis_pid=$(get_pid_on_port "$REDIS_PORT")
        print_success "Redis: CORRIENDO (PID: $redis_pid, Puerto: $REDIS_PORT)"
        if command_exists redis-cli && redis-cli ping >/dev/null 2>&1; then
            echo -e "   ${GREEN}✓${NC} Health check: OK"
        fi
    else
        print_error "Redis: NO ESTÁ CORRIENDO"
    fi
    
    echo ""
    
    # Celery
    if pgrep -f "celery.*worker" >/dev/null 2>&1; then
        local celery_pid=$(pgrep -f "celery.*worker" | head -1)
        print_success "Celery: CORRIENDO (PID: $celery_pid)"
    else
        print_error "Celery: NO ESTÁ CORRIENDO"
    fi
    
    echo ""
    
    # Backend
    if port_in_use "$BACKEND_PORT"; then
        local backend_pid=$(get_pid_on_port "$BACKEND_PORT")
        print_success "Backend: CORRIENDO (PID: $backend_pid, Puerto: $BACKEND_PORT)"
        if curl -s "$BACKEND_URL/api/v1/system/health" >/dev/null 2>&1; then
            echo -e "   ${GREEN}✓${NC} Health check: OK"
        else
            echo -e "   ${YELLOW}⚠${NC} Health check: No responde"
        fi
    else
        print_error "Backend: NO ESTÁ CORRIENDO"
    fi
    
    echo ""
    
    # Frontend
    if port_in_use "$FRONTEND_PORT"; then
        local frontend_pid=$(get_pid_on_port "$FRONTEND_PORT")
        print_success "Frontend: CORRIENDO (PID: $frontend_pid, Puerto: $FRONTEND_PORT)"
        if curl -s "$FRONTEND_URL" >/dev/null 2>&1; then
            echo -e "   ${GREEN}✓${NC} Responde correctamente"
        else
            echo -e "   ${YELLOW}⚠${NC} Puede estar compilando..."
        fi
    else
        print_error "Frontend: NO ESTÁ CORRIENDO"
    fi
    
    echo ""
}

show_logs() {
    print_header "📄 LOGS DE SERVICIOS"
    
    # Backend: mostrar app.log (sistema de logging de Python con rotación)
    local backend_log="$BACKEND_DIR/logs/app.log"
    if [[ -f "$backend_log" ]]; then
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${CYAN}Backend Log (app.log - últimas 30 líneas):${NC}"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        tail -30 "$backend_log"
        echo ""
    else
        print_warning "No hay logs de backend (app.log no encontrado)"
    fi
    
    # También mostrar startup log si existe (solo errores de inicio)
    if [[ -f "$LOG_DIR/backend_startup.log" ]]; then
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${CYAN}Backend Startup Log (últimas 20 líneas):${NC}"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        tail -20 "$LOG_DIR/backend_startup.log"
        echo ""
    fi
    
    if [[ -f "$LOG_DIR/celery.log" ]]; then
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${CYAN}Celery Log (últimas 30 líneas):${NC}"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        tail -30 "$LOG_DIR/celery.log"
        echo ""
    else
        print_warning "No hay logs de Celery"
    fi
    
    if [[ -f "$LOG_DIR/frontend.log" ]]; then
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${CYAN}Frontend Log (últimas 30 líneas):${NC}"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        tail -30 "$LOG_DIR/frontend.log"
        echo ""
    else
        print_warning "No hay logs de frontend"
    fi
}

# ==============================================================================
# MAIN
# ==============================================================================

main() {
    case "${1:-start}" in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        restart)
            stop_services
            sleep 2
            start_services
            ;;
        *)
            echo "Uso: $0 {start|stop|status|logs|restart}"
            echo ""
            echo "Comandos:"
            echo "  start   - Iniciar servicios (por defecto)"
            echo "  stop    - Detener servicios"
            echo "  status  - Ver estado de servicios"
            echo "  logs    - Ver logs de servicios"
            echo "  restart - Reiniciar servicios"
            exit 1
            ;;
    esac
}

# Ejecutar main
main "$@"

