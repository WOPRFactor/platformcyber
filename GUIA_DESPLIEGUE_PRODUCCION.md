# Guía de Despliegue en Producción - Máquina Separada

**Fecha:** Enero 2025  
**Objetivo:** Guía completa para desplegar dev4-improvements en una máquina de producción separada

---

## 📊 RESUMEN EJECUTIVO

**Separación de Entornos:**
- 🖥️ **Máquina Actual:** Desarrollo (dev4-improvements)
- 🚀 **Máquina Nueva:** Producción (separada físicamente)

**Ventajas:**
- ✅ Aislamiento completo de desarrollo y producción
- ✅ Mejor seguridad (producción no expuesta durante desarrollo)
- ✅ Mejor rendimiento (recursos dedicados)
- ✅ Facilita backups y mantenimiento

---

## 🖥️ REQUISITOS DE LA MÁQUINA DE PRODUCCIÓN

### **Especificaciones Mínimas Recomendadas**

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **CPU** | 4 núcleos | 8+ núcleos |
| **RAM** | 8GB | 16GB+ |
| **Almacenamiento** | 50GB SSD | 100GB+ SSD |
| **Red** | 100 Mbps | 1 Gbps |
| **SO** | Ubuntu 22.04 LTS / Debian 12 | Ubuntu 22.04 LTS |

### **Software Requerido**

```bash
# Sistema operativo base
- Ubuntu 22.04 LTS o Debian 12 (recomendado)
- O Kali Linux si necesitas herramientas de seguridad preinstaladas

# Software base
- Docker 24.0+ y Docker Compose 2.0+
- Git
- curl, wget
- firewall (ufw o iptables)
```

---

## 📦 PASO 1: PREPARAR LA MÁQUINA DE PRODUCCIÓN

### 1.1 Instalar Docker y Docker Compose

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Agregar repositorio Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Agregar usuario al grupo docker (opcional, para no usar sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verificar instalación
docker --version
docker compose version
```

### 1.2 Configurar Firewall

```bash
# Instalar UFW si no está instalado
sudo apt install -y ufw

# Permitir SSH (IMPORTANTE: hacerlo primero)
sudo ufw allow 22/tcp

# Permitir HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Permitir puertos específicos si no usas reverse proxy
# sudo ufw allow 5000/tcp  # Backend (solo si acceso directo)

# Activar firewall
sudo ufw enable
sudo ufw status
```

### 1.3 Crear Estructura de Directorios

```bash
# Crear directorio del proyecto
sudo mkdir -p /opt/cybersecurity-platform
sudo chown $USER:$USER /opt/cybersecurity-platform
cd /opt/cybersecurity-platform

# Crear estructura de directorios
mkdir -p {workspaces,logs,backups,ssl,nginx}
```

---

## 📋 PASO 2: TRANSFERIR CÓDIGO Y CONFIGURACIÓN

### 2.1 Opción A: Clonar desde Git (Recomendado)

```bash
# En la máquina de producción
cd /opt/cybersecurity-platform

# Clonar repositorio (ajustar URL según tu repo)
git clone <URL_DEL_REPOSITORIO> .

# O si ya tienes el código en la máquina de desarrollo:
# Usar rsync o scp para transferir
```

### 2.2 Opción B: Transferir desde Máquina de Desarrollo

```bash
# En la máquina de DESARROLLO (desde donde copias)
cd /home/kali/Proyectos/cybersecurity/environments/dev4-improvements

# Crear archivo comprimido (excluyendo venv, node_modules, etc.)
tar --exclude='venv' \
    --exclude='node_modules' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.db' \
    --exclude='logs' \
    -czf ../dev4-production.tar.gz platform/ docker-compose.prod.yml

# Transferir a máquina de producción
scp ../dev4-production.tar.gz usuario@maquina-produccion:/tmp/

# En la máquina de PRODUCCIÓN
cd /opt/cybersecurity-platform
tar -xzf /tmp/dev4-production.tar.gz
rm /tmp/dev4-production.tar.gz
```

---

## 🔐 PASO 3: CONFIGURAR VARIABLES DE ENTORNO

### 3.1 Crear Archivo `.env` para Producción

```bash
# En la máquina de producción
cd /opt/cybersecurity-platform
nano .env
```

**Contenido del archivo `.env`:**

```bash
# ============================================
# PRODUCCIÓN - Cybersecurity Platform
# ============================================

# Ambiente
FLASK_ENV=production
FLASK_DEBUG=0

# ============================================
# SEGURIDAD (GENERAR NUEVOS SECRETS)
# ============================================
# Generar con: openssl rand -hex 32
SECRET_KEY=<GENERAR_SECRET_UNICO>
JWT_SECRET_KEY=<GENERAR_SECRET_UNICO>

# ============================================
# BASE DE DATOS
# ============================================
POSTGRES_DB=pentesting_platform_prod
POSTGRES_USER=pentest_user
POSTGRES_PASSWORD=<GENERAR_PASSWORD_SEGURO>
DATABASE_URL=postgresql://pentest_user:<PASSWORD>@db:5432/pentesting_platform_prod

# ============================================
# REDIS
# ============================================
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# ============================================
# CORS (Solo dominios permitidos)
# ============================================
CORS_ORIGINS=https://pentest.tudominio.com,https://www.pentest.tudominio.com

# ============================================
# WORKSPACES Y ARCHIVOS
# ============================================
WORKSPACES_BASE_DIR=/opt/cybersecurity-platform/workspaces
PROJECT_TMP_DIR=/opt/cybersecurity-platform/tmp

# ============================================
# LOGGING
# ============================================
LOG_DIR=/opt/cybersecurity-platform/logs
LOG_FILE=app.log
LOG_LEVEL=INFO

# ============================================
# RATE LIMITING
# ============================================
RATE_LIMIT_ENABLED=true

# ============================================
# GRAFANA (Opcional)
# ============================================
GRAFANA_USER=admin
GRAFANA_PASSWORD=<GENERAR_PASSWORD>
```

### 3.2 Generar Secrets Seguros

```bash
# Generar SECRET_KEY
openssl rand -hex 32

# Generar JWT_SECRET_KEY
openssl rand -hex 32

# Generar contraseña PostgreSQL
openssl rand -base64 24

# Generar contraseña Grafana
openssl rand -base64 16
```

**⚠️ IMPORTANTE:** Guardar estos secrets en un lugar seguro (gestor de contraseñas, vault, etc.)

---

## 🐳 PASO 4: CONFIGURAR DOCKER COMPOSE PARA PRODUCCIÓN

### 4.1 Ajustar `docker-compose.prod.yml`

El archivo ya existe, pero verificar estas configuraciones:

```yaml
# Verificar que los volúmenes apunten a rutas correctas
volumes:
  - /opt/cybersecurity-platform/workspaces:/workspaces:rw
  - /opt/cybersecurity-platform/tmp:/tmp/scans:rw
  - /opt/cybersecurity-platform/logs:/app/logs:rw
```

### 4.2 Crear Configuración de Nginx (si no existe)

```bash
mkdir -p nginx
nano nginx/nginx.conf
```

**Contenido `nginx/nginx.conf`:**

```nginx
upstream backend {
    server backend:5000;
}

upstream frontend {
    server frontend:80;
}

server {
    listen 80;
    server_name pentest.tudominio.com;
    
    # Redirigir HTTP a HTTPS (descomentar cuando tengas SSL)
    # return 301 https://$server_name$request_uri;
    
    # O servir directamente si no tienes SSL aún
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Descomentar cuando tengas SSL
# server {
#     listen 443 ssl http2;
#     server_name pentest.tudominio.com;
#     
#     ssl_certificate /etc/nginx/ssl/cert.pem;
#     ssl_certificate_key /etc/nginx/ssl/key.pem;
#     
#     location / {
#         proxy_pass http://frontend;
#         ...
#     }
#     
#     location /api {
#         proxy_pass http://backend;
#         ...
#     }
# }
```

---

## 🚀 PASO 5: DESPLEGAR LA APLICACIÓN

### 5.1 Construir y Levantar Servicios

```bash
cd /opt/cybersecurity-platform

# Construir imágenes
docker compose -f docker-compose.prod.yml build

# Levantar servicios en background
docker compose -f docker-compose.prod.yml up -d

# Ver logs
docker compose -f docker-compose.prod.yml logs -f

# Ver estado
docker compose -f docker-compose.prod.yml ps
```

### 5.2 Verificar que Todo Funciona

```bash
# Verificar contenedores
docker ps

# Verificar logs del backend
docker logs pentesting-backend-prod

# Verificar logs del frontend
docker logs pentesting-frontend-prod

# Verificar conectividad
curl http://localhost/api/v1/health
```

### 5.3 Inicializar Base de Datos

```bash
# Ejecutar migraciones (si las hay)
docker exec -it pentesting-backend-prod python -m flask db upgrade

# O crear usuario admin inicial
docker exec -it pentesting-backend-prod python create_admin.py
```

---

## 🔒 PASO 6: CONFIGURAR SSL/TLS (Opcional pero Recomendado)

### 6.1 Usando Let's Encrypt (Certbot)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d pentest.tudominio.com

# Renovación automática
sudo certbot renew --dry-run
```

### 6.2 Configurar Renovación Automática

```bash
# Agregar a crontab
sudo crontab -e

# Agregar línea:
0 0 * * * certbot renew --quiet --deploy-hook "docker compose -f /opt/cybersecurity-platform/docker-compose.prod.yml restart nginx"
```

---

## 📊 PASO 7: CONFIGURAR MONITOREO Y BACKUPS

### 7.1 Script de Backup Automático

```bash
# Crear script de backup
nano /opt/cybersecurity-platform/backup.sh
```

**Contenido:**

```bash
#!/bin/bash
BACKUP_DIR="/opt/cybersecurity-platform/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup de base de datos
docker exec pentesting-db-prod pg_dump -U pentest_user pentesting_platform_prod > "$BACKUP_DIR/db_$DATE.sql"

# Backup de workspaces
tar -czf "$BACKUP_DIR/workspaces_$DATE.tar.gz" /opt/cybersecurity-platform/workspaces

# Eliminar backups antiguos (mantener últimos 7 días)
find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "Backup completado: $DATE"
```

```bash
# Hacer ejecutable
chmod +x /opt/cybersecurity-platform/backup.sh

# Agregar a crontab (backup diario a las 2 AM)
crontab -e
# Agregar:
0 2 * * * /opt/cybersecurity-platform/backup.sh >> /opt/cybersecurity-platform/logs/backup.log 2>&1
```

### 7.2 Monitoreo con Prometheus/Grafana

El `docker-compose.prod.yml` ya incluye Prometheus y Grafana. Solo necesitas:

```bash
# Acceder a Grafana
# http://tu-servidor:3000
# Usuario: admin (o el configurado en GRAFANA_USER)
# Password: (el configurado en GRAFANA_PASSWORD)
```

---

## 🔄 PASO 8: ACTUALIZACIONES Y MANTENIMIENTO

### 8.1 Actualizar Código

```bash
# Si usas Git
cd /opt/cybersecurity-platform
git pull origin main

# Reconstruir y reiniciar
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

### 8.2 Ver Logs

```bash
# Todos los servicios
docker compose -f docker-compose.prod.yml logs -f

# Servicio específico
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f celery-worker
```

### 8.3 Reiniciar Servicios

```bash
# Reiniciar todo
docker compose -f docker-compose.prod.yml restart

# Reiniciar servicio específico
docker compose -f docker-compose.prod.yml restart backend
```

---

## ✅ CHECKLIST DE DESPLIEGUE

### Pre-despliegue
- [ ] Máquina de producción preparada (Docker instalado)
- [ ] Firewall configurado
- [ ] Estructura de directorios creada
- [ ] Código transferido

### Configuración
- [ ] Archivo `.env` creado con todos los secrets
- [ ] Secrets generados y guardados de forma segura
- [ ] `docker-compose.prod.yml` ajustado
- [ ] Nginx configurado (si aplica)

### Despliegue
- [ ] Imágenes Docker construidas
- [ ] Servicios levantados y funcionando
- [ ] Base de datos inicializada
- [ ] Health checks pasando

### Post-despliegue
- [ ] SSL/TLS configurado (opcional)
- [ ] Backups automáticos configurados
- [ ] Monitoreo funcionando
- [ ] Documentación de acceso guardada

---

## 🆘 TROUBLESHOOTING COMÚN

### Problema: Contenedores no inician

```bash
# Ver logs detallados
docker compose -f docker-compose.prod.yml logs

# Verificar variables de entorno
docker exec pentesting-backend-prod env | grep DATABASE_URL
```

### Problema: Base de datos no conecta

```bash
# Verificar que PostgreSQL está corriendo
docker ps | grep postgres

# Verificar conexión
docker exec -it pentesting-db-prod psql -U pentest_user -d pentesting_platform_prod
```

### Problema: Permisos en volúmenes

```bash
# Ajustar permisos
sudo chown -R $USER:$USER /opt/cybersecurity-platform/workspaces
sudo chown -R $USER:$USER /opt/cybersecurity-platform/logs
```

---

## 📝 NOTAS IMPORTANTES

1. **Separación de Entornos:**
   - ✅ Desarrollo en máquina actual (dev4-improvements)
   - ✅ Producción en máquina nueva (completamente separada)

2. **Seguridad:**
   - 🔒 Nunca compartir secrets entre desarrollo y producción
   - 🔒 Usar contraseñas fuertes y únicas
   - 🔒 Configurar firewall correctamente
   - 🔒 Usar SSL/TLS en producción

3. **Backups:**
   - 💾 Configurar backups automáticos
   - 💾 Probar restauración periódicamente
   - 💾 Guardar backups fuera del servidor

4. **Monitoreo:**
   - 📊 Configurar alertas
   - 📊 Revisar logs regularmente
   - 📊 Monitorear recursos (CPU, RAM, disco)

---

**Documento generado:** Enero 2025  
**Última actualización:** Enero 2025

