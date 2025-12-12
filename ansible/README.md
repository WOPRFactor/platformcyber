# Ansible Playbook - Despliegue Cybersecurity Platform en Kali Linux

**Objetivo:** Automatizar el despliegue completo de la plataforma Cybersecurity en Kali Linux **SIN Docker**, separando entornos dev/prod.

---

## 📋 REQUISITOS PREVIOS

### En la Máquina de Control (donde ejecutas Ansible)

```bash
# Instalar Ansible
sudo apt update
sudo apt install -y ansible

# Verificar instalación
ansible --version
```

### En la Máquina Remota (Kali Linux donde se despliega)

- ✅ Kali Linux instalado
- ✅ Acceso SSH configurado
- ✅ Usuario con permisos sudo
- ✅ **Código fuente ya descargado** (desde GitHub o transferido)

---

## 🚀 USO RÁPIDO

### 1. Configurar Inventario

Editar `inventory/hosts.ini`:

```ini
[kali_servers]
192.168.1.100 ansible_user=kali ansible_ssh_private_key_file=~/.ssh/id_rsa

[kali_servers:vars]
# Password de PostgreSQL admin (opcional)
postgres_admin_password=
# Password para BD del entorno (se generará si no se especifica)
db_password=changeme
```

### 2. Ejecutar Playbook

```bash
# Desplegar entorno DEV
ansible-playbook -i inventory/hosts.ini deploy-kali.yml -e "environment=dev"

# Desplegar entorno PROD
ansible-playbook -i inventory/hosts.ini deploy-kali.yml -e "environment=prod"
```

### 3. Verificar Despliegue

```bash
# En la máquina remota
supervisorctl status
curl http://localhost:5001/api/v1/health  # DEV
curl http://localhost:5002/api/v1/health  # PROD
```

---

## 📁 ESTRUCTURA DEL PROYECTO

```
ansible/
├── deploy-kali.yml              # Playbook principal
├── inventory/
│   └── hosts.ini                # Inventario de servidores
├── templates/
│   ├── backend.env.j2           # Variables de entorno backend
│   ├── frontend.env.j2          # Variables de entorno frontend
│   ├── supervisor-backend.conf.j2
│   ├── supervisor-frontend.conf.j2
│   ├── supervisor-celery.conf.j2
│   ├── redis-dev.conf.j2
│   ├── redis-prod.conf.j2
│   ├── redis-dev.service.j2
│   └── redis-prod.service.j2
└── README.md
```

---

## 🔧 CONFIGURACIÓN DETALLADA

### Variables del Playbook

El playbook usa estas variables (configurables):

| Variable | Descripción | Default |
|----------|-------------|---------|
| `environment` | Entorno a desplegar (dev/prod) | dev |
| `project_base_dir` | Directorio base del proyecto | `/opt/cybersecurity-platform` |
| `app_user` | Usuario que ejecuta la app | Usuario SSH actual |
| `python_version` | Versión de Python | 3.11 |
| `node_version` | Versión de Node.js | 20 |
| `db_password` | Password de BD del entorno | changeme |
| `postgres_admin_password` | Password admin PostgreSQL | (vacío) |

### Puertos por Entorno

| Servicio | DEV | PROD |
|----------|-----|------|
| Backend | 5001 | 5002 |
| Frontend | 5180 | 5181 |
| Redis | 6379 | 6380 |
| PostgreSQL | 5432 | 5433 |

### Directorios Creados

```
/opt/cybersecurity-platform/
├── environments/
│   ├── dev/
│   │   ├── platform/
│   │   │   ├── backend/     # Código backend + venv
│   │   │   └── frontend/    # Código frontend + node_modules
│   │   ├── workspaces/      # Workspaces de usuarios
│   │   ├── logs/            # Logs de la aplicación
│   │   └── tmp/             # Archivos temporales
│   └── prod/
│       └── (misma estructura)
```

---

## 📝 PASOS QUE EJECUTA EL PLAYBOOK

1. ✅ **Actualizar sistema** - `apt update && apt upgrade`
2. ✅ **Instalar dependencias** - Python, Node.js, PostgreSQL, Redis, Supervisor, etc.
3. ✅ **Crear estructura de directorios** - Workspaces, logs, tmp
4. ✅ **Copiar código** - Desde ubicación encontrada al entorno
5. ✅ **Configurar Python venv** - Crear e instalar dependencias
6. ✅ **Instalar dependencias Node.js** - npm install
7. ✅ **Configurar PostgreSQL** - Crear BD y usuario
8. ✅ **Configurar Redis** - Instancia separada por entorno
9. ✅ **Generar secrets** - SECRET_KEY, JWT_SECRET_KEY automáticos
10. ✅ **Crear archivos .env** - Variables de entorno
11. ✅ **Configurar Supervisor** - Backend, Frontend, Celery
12. ✅ **Configurar Firewall** - UFW con puertos necesarios
13. ✅ **Inicializar BD** - Migraciones y usuario admin
14. ✅ **Iniciar servicios** - Todo con Supervisor

---

## 🔐 SEGURIDAD

### Secrets Generados Automáticamente

El playbook genera automáticamente:
- `SECRET_KEY` - Con `openssl rand -hex 32`
- `JWT_SECRET_KEY` - Con `openssl rand -hex 32`

**⚠️ IMPORTANTE:** Estos secrets se guardan en `.env`. Asegúrate de:
- No commitear `.env` a Git
- Hacer backup de los secrets
- Usar secrets diferentes para dev y prod

### Firewall

El playbook configura UFW para permitir:
- Puerto 22 (SSH)
- Puerto backend del entorno
- Puerto frontend del entorno

---

## 🐛 TROUBLESHOOTING

### Error: "No se encontró el código fuente"

**Solución:** Asegúrate de tener el código en una de estas ubicaciones:
- `/opt/cybersecurity-platform/source/platform/`
- `~/cybersecurity-platform/platform/`
- `/home/kali/cybersecurity-platform/platform/`

O copia manualmente antes de ejecutar:
```bash
# En la máquina remota
mkdir -p /opt/cybersecurity-platform/source
cp -r /ruta/a/tu/codigo/platform /opt/cybersecurity-platform/source/
```

### Error: "requirements.txt no encontrado"

**Solución:** Verifica que el código se copió correctamente:
```bash
ls -la /opt/cybersecurity-platform/environments/dev/platform/backend/requirements.txt
```

### Error: PostgreSQL no inicia

**Solución:** Verificar servicio:
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### Error: Supervisor no inicia servicios

**Solución:** Ver logs y estado:
```bash
sudo supervisorctl status
sudo tail -f /opt/cybersecurity-platform/environments/dev/logs/backend.log
```

### Error: Permisos denegados

**Solución:** Ajustar permisos:
```bash
sudo chown -R kali:kali /opt/cybersecurity-platform/environments/dev/
```

---

## 🔄 ACTUALIZAR CÓDIGO

Si necesitas actualizar el código después del despliegue inicial:

```bash
# Opción 1: Desde Git (si tienes repo)
cd /opt/cybersecurity-platform/source
git pull

# Opción 2: Copiar nuevo código manualmente
# Luego ejecutar solo las tareas de instalación:
ansible-playbook -i inventory/hosts.ini deploy-kali.yml \
  -e "environment=dev" \
  --tags "dependencies,services" \
  --skip-tags "system,postgresql,redis"
```

---

## 📊 VERIFICAR ESTADO

### En la Máquina Remota

```bash
# Estado de servicios Supervisor
supervisorctl status

# Logs del backend
tail -f /opt/cybersecurity-platform/environments/dev/logs/backend.log

# Logs del frontend
tail -f /opt/cybersecurity-platform/environments/dev/logs/frontend.log

# Logs de Celery
tail -f /opt/cybersecurity-platform/environments/dev/logs/celery.log

# Estado de PostgreSQL
sudo systemctl status postgresql

# Estado de Redis
sudo systemctl status redis-dev  # o redis-prod
```

### Desde Máquina de Control

```bash
# Verificar salud del backend
ansible kali_servers -i inventory/hosts.ini \
  -m uri -a "url=http://localhost:5001/api/v1/health"
```

---

## 🎯 EJEMPLOS DE USO

### Desplegar Solo DEV

```bash
ansible-playbook -i inventory/hosts.ini deploy-kali.yml -e "environment=dev"
```

### Desplegar Solo PROD

```bash
ansible-playbook -i inventory/hosts.ini deploy-kali.yml -e "environment=prod"
```

### Desplegar Ambos Entornos

```bash
ansible-playbook -i inventory/hosts.ini deploy-kali.yml -e "environment=dev"
ansible-playbook -i inventory/hosts.ini deploy-kali.yml -e "environment=prod"
```

### Solo Instalar Dependencias (sin reiniciar servicios)

```bash
ansible-playbook -i inventory/hosts.ini deploy-kali.yml \
  -e "environment=dev" \
  --tags "dependencies"
```

### Solo Configurar Servicios (asume dependencias instaladas)

```bash
ansible-playbook -i inventory/hosts.ini deploy-kali.yml \
  -e "environment=dev" \
  --tags "services,supervisor"
```

---

## 📚 REFERENCIAS

- [Documentación Ansible](https://docs.ansible.com/)
- [Supervisor Documentation](http://supervisord.org/)
- [PostgreSQL Ansible Modules](https://docs.ansible.com/ansible/latest/collections/community/postgresql/)

---

**Autor:** Factor X  
**Fecha:** Enero 2025  
**Versión:** 1.0.0
