"""
MITRE ATT&CK Techniques Data
============================

Datos de técnicas MITRE ATT&CK (subset importante).
"""

from typing import Dict, Any


def get_techniques() -> Dict[str, Dict[str, Any]]:
    """Obtener todas las técnicas MITRE ATT&CK"""
    return {
        # === RECONNAISSANCE ===
        'T1595': {
            'id': 'T1595',
            'name': 'Active Scanning',
            'tactic': 'TA0043',
            'description': 'Escaneo activo de infraestructura objetivo',
            'detection': 'Monitoreo de logs de firewall, IDS/IPS',
            'platforms': ['Linux', 'Windows', 'Network'],
            'data_sources': ['Network Traffic', 'Network Traffic Content']
        },
        'T1592': {
            'id': 'T1592',
            'name': 'Gather Victim Host Information',
            'tactic': 'TA0043',
            'description': 'Recopilar información sobre hosts de la víctima',
            'detection': 'Monitoreo de consultas DNS anómalas',
            'platforms': ['PRE'],
            'data_sources': ['Internet Scan']
        },
        
        # === INITIAL ACCESS ===
        'T1566': {
            'id': 'T1566',
            'name': 'Phishing',
            'tactic': 'TA0001',
            'description': 'Envío de correos de phishing',
            'detection': 'Email gateway, análisis de attachments',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['Application Log', 'File', 'Network Traffic']
        },
        'T1190': {
            'id': 'T1190',
            'name': 'Exploit Public-Facing Application',
            'tactic': 'TA0001',
            'description': 'Explotar aplicaciones expuestas',
            'detection': 'WAF logs, análisis de anomalías',
            'platforms': ['Linux', 'Windows', 'Network'],
            'data_sources': ['Application Log', 'Network Traffic']
        },
        'T1133': {
            'id': 'T1133',
            'name': 'External Remote Services',
            'tactic': 'TA0001',
            'description': 'Acceso mediante servicios remotos (VPN, RDP)',
            'detection': 'Logs de autenticación, geolocalización',
            'platforms': ['Windows', 'Linux'],
            'data_sources': ['Logon Session', 'Network Traffic']
        },
        
        # === EXECUTION ===
        'T1059': {
            'id': 'T1059',
            'name': 'Command and Scripting Interpreter',
            'tactic': 'TA0002',
            'description': 'Ejecución vía intérpretes (PowerShell, bash, etc)',
            'detection': 'Process monitoring, command line logging',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['Command', 'Process', 'Script']
        },
        'T1203': {
            'id': 'T1203',
            'name': 'Exploitation for Client Execution',
            'tactic': 'TA0002',
            'description': 'Explotar vulnerabilidades de software cliente',
            'detection': 'Endpoint detection, behavior analysis',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['Application Log', 'Process']
        },
        'T1569': {
            'id': 'T1569',
            'name': 'System Services',
            'tactic': 'TA0002',
            'description': 'Abuso de servicios del sistema',
            'detection': 'Service creation/modification monitoring',
            'platforms': ['Windows', 'Linux'],
            'data_sources': ['Service', 'Process', 'Command']
        },
        
        # === PERSISTENCE ===
        'T1053': {
            'id': 'T1053',
            'name': 'Scheduled Task/Job',
            'tactic': 'TA0003',
            'description': 'Tareas programadas para persistencia',
            'detection': 'Scheduled task logs, cron monitoring',
            'platforms': ['Windows', 'Linux', 'macOS'],
            'data_sources': ['Scheduled Job', 'Command', 'Process']
        },
        'T1136': {
            'id': 'T1136',
            'name': 'Create Account',
            'tactic': 'TA0003',
            'description': 'Crear cuentas de usuario',
            'detection': 'Account creation logs',
            'platforms': ['Windows', 'Linux', 'macOS'],
            'data_sources': ['User Account', 'Process', 'Command']
        },
        'T1543': {
            'id': 'T1543',
            'name': 'Create or Modify System Process',
            'tactic': 'TA0003',
            'description': 'Crear/modificar servicios del sistema',
            'detection': 'Service monitoring, registry changes',
            'platforms': ['Windows', 'Linux', 'macOS'],
            'data_sources': ['Service', 'Windows Registry', 'Process']
        },
        
        # === PRIVILEGE ESCALATION ===
        'T1068': {
            'id': 'T1068',
            'name': 'Exploitation for Privilege Escalation',
            'tactic': 'TA0004',
            'description': 'Explotar vulnerabilidades para escalar privilegios',
            'detection': 'Behavior analysis, exploit detection',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['Process', 'Application Log']
        },
        'T1078': {
            'id': 'T1078',
            'name': 'Valid Accounts',
            'tactic': 'TA0004',
            'description': 'Uso de cuentas válidas para escalar',
            'detection': 'Login anomalies, privilege usage',
            'platforms': ['Windows', 'Linux', 'macOS'],
            'data_sources': ['Logon Session', 'User Account']
        },
        
        # === DEFENSE EVASION ===
        'T1027': {
            'id': 'T1027',
            'name': 'Obfuscated Files or Information',
            'tactic': 'TA0005',
            'description': 'Ofuscar archivos o información',
            'detection': 'File analysis, entropy detection',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['File', 'Script', 'Command']
        },
        'T1070': {
            'id': 'T1070',
            'name': 'Indicator Removal',
            'tactic': 'TA0005',
            'description': 'Eliminar indicadores de compromiso',
            'detection': 'Log monitoring, file integrity',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['File', 'Process', 'Command']
        },
        'T1055': {
            'id': 'T1055',
            'name': 'Process Injection',
            'tactic': 'TA0005',
            'description': 'Inyectar código en procesos legítimos',
            'detection': 'Process behavior analysis, memory monitoring',
            'platforms': ['Windows', 'Linux', 'macOS'],
            'data_sources': ['Process', 'Module']
        },
        'T1562': {
            'id': 'T1562',
            'name': 'Impair Defenses',
            'tactic': 'TA0005',
            'description': 'Deshabilitar controles de seguridad',
            'detection': 'Security tool monitoring, service status',
            'platforms': ['Windows', 'Linux', 'macOS'],
            'data_sources': ['Service', 'Process', 'Command', 'Windows Registry']
        },
        
        # === CREDENTIAL ACCESS ===
        'T1110': {
            'id': 'T1110',
            'name': 'Brute Force',
            'tactic': 'TA0006',
            'description': 'Fuerza bruta de credenciales',
            'detection': 'Failed login attempts, rate limiting',
            'platforms': ['Windows', 'Linux', 'macOS', 'Network'],
            'data_sources': ['Logon Session', 'User Account']
        },
        'T1003': {
            'id': 'T1003',
            'name': 'OS Credential Dumping',
            'tactic': 'TA0006',
            'description': 'Dump de credenciales del SO',
            'detection': 'LSASS monitoring, SAM access',
            'platforms': ['Windows', 'Linux', 'macOS'],
            'data_sources': ['Process', 'Command', 'File']
        },
        'T1056': {
            'id': 'T1056',
            'name': 'Input Capture',
            'tactic': 'TA0006',
            'description': 'Captura de input del usuario (keylogging)',
            'detection': 'Behavior analysis, API monitoring',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['Process', 'Driver', 'Windows Registry']
        },
        
        # === DISCOVERY ===
        'T1083': {
            'id': 'T1083',
            'name': 'File and Directory Discovery',
            'tactic': 'TA0007',
            'description': 'Enumeración de archivos y directorios',
            'detection': 'File access monitoring',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['Process', 'Command', 'File']
        },
        'T1087': {
            'id': 'T1087',
            'name': 'Account Discovery',
            'tactic': 'TA0007',
            'description': 'Descubrir cuentas del sistema',
            'detection': 'Command monitoring, API calls',
            'platforms': ['Windows', 'Linux', 'macOS'],
            'data_sources': ['Command', 'Process', 'Group']
        },
        'T1018': {
            'id': 'T1018',
            'name': 'Remote System Discovery',
            'tactic': 'TA0007',
            'description': 'Identificar sistemas remotos',
            'detection': 'Network monitoring, command analysis',
            'platforms': ['Windows', 'Linux', 'macOS'],
            'data_sources': ['Network Traffic', 'Command', 'Process']
        },
        'T1046': {
            'id': 'T1046',
            'name': 'Network Service Discovery',
            'tactic': 'TA0007',
            'description': 'Escaneo de servicios de red',
            'detection': 'Network traffic analysis',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['Network Traffic', 'Command']
        },
        
        # === LATERAL MOVEMENT ===
        'T1021': {
            'id': 'T1021',
            'name': 'Remote Services',
            'tactic': 'TA0008',
            'description': 'Uso de servicios remotos (RDP, SSH, WinRM)',
            'detection': 'Authentication logs, network monitoring',
            'platforms': ['Windows', 'Linux', 'macOS'],
            'data_sources': ['Logon Session', 'Network Traffic', 'Process']
        },
        'T1080': {
            'id': 'T1080',
            'name': 'Taint Shared Content',
            'tactic': 'TA0008',
            'description': 'Contaminar contenido compartido',
            'detection': 'File integrity monitoring',
            'platforms': ['Windows', 'Linux'],
            'data_sources': ['File', 'Network Traffic']
        },
        
        # === COLLECTION ===
        'T1005': {
            'id': 'T1005',
            'name': 'Data from Local System',
            'tactic': 'TA0009',
            'description': 'Recolectar datos del sistema local',
            'detection': 'File access monitoring, DLP',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['File', 'Command', 'Process']
        },
        'T1560': {
            'id': 'T1560',
            'name': 'Archive Collected Data',
            'tactic': 'TA0009',
            'description': 'Archivar datos recolectados',
            'detection': 'File creation, compression tools',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['File', 'Command', 'Process']
        },
        'T1113': {
            'id': 'T1113',
            'name': 'Screen Capture',
            'tactic': 'TA0009',
            'description': 'Captura de pantalla',
            'detection': 'API monitoring, behavior analysis',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['Command', 'Process']
        },
        
        # === COMMAND AND CONTROL ===
        'T1071': {
            'id': 'T1071',
            'name': 'Application Layer Protocol',
            'tactic': 'TA0011',
            'description': 'C2 sobre protocolos de aplicación (HTTP, DNS)',
            'detection': 'Network traffic analysis, behavioral anomalies',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['Network Traffic', 'Network Traffic Content']
        },
        'T1573': {
            'id': 'T1573',
            'name': 'Encrypted Channel',
            'tactic': 'TA0011',
            'description': 'Cifrar canal C2',
            'detection': 'Certificate analysis, traffic inspection',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['Network Traffic']
        },
        'T1219': {
            'id': 'T1219',
            'name': 'Remote Access Software',
            'tactic': 'TA0011',
            'description': 'Uso de software de acceso remoto',
            'detection': 'Software installation monitoring',
            'platforms': ['Windows', 'Linux', 'macOS'],
            'data_sources': ['Process', 'Network Traffic']
        },
        
        # === EXFILTRATION ===
        'T1041': {
            'id': 'T1041',
            'name': 'Exfiltration Over C2 Channel',
            'tactic': 'TA0010',
            'description': 'Exfiltración sobre canal C2',
            'detection': 'Network traffic volume analysis',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['Network Traffic', 'Network Traffic Content']
        },
        'T1048': {
            'id': 'T1048',
            'name': 'Exfiltration Over Alternative Protocol',
            'tactic': 'TA0010',
            'description': 'Exfiltración por protocolo alternativo',
            'detection': 'Network monitoring, DLP',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['Network Traffic', 'Network Traffic Content']
        },
        
        # === IMPACT ===
        'T1486': {
            'id': 'T1486',
            'name': 'Data Encrypted for Impact',
            'tactic': 'TA0040',
            'description': 'Cifrar datos (ransomware)',
            'detection': 'File modification monitoring, behavior analysis',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['File', 'Process', 'Command']
        },
        'T1490': {
            'id': 'T1490',
            'name': 'Inhibit System Recovery',
            'tactic': 'TA0040',
            'description': 'Impedir recuperación del sistema',
            'detection': 'Backup deletion monitoring',
            'platforms': ['Windows', 'Linux', 'macOS'],
            'data_sources': ['Command', 'Process', 'File']
        },
        'T1498': {
            'id': 'T1498',
            'name': 'Network Denial of Service',
            'tactic': 'TA0040',
            'description': 'DoS de red',
            'detection': 'Network traffic analysis, IDS',
            'platforms': ['Linux', 'Windows', 'macOS', 'Network'],
            'data_sources': ['Network Traffic', 'Sensor Health']
        },
        'T1529': {
            'id': 'T1529',
            'name': 'System Shutdown/Reboot',
            'tactic': 'TA0040',
            'description': 'Apagar/reiniciar sistemas',
            'detection': 'System event logs',
            'platforms': ['Linux', 'Windows', 'macOS'],
            'data_sources': ['Command', 'Process']
        }
    }


