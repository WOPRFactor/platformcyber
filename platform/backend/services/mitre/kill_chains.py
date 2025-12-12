"""
MITRE ATT&CK Kill Chains Data
==============================

Datos de kill chains predefinidos de APTs conocidos.
"""

from typing import Dict, Any


def get_kill_chains() -> Dict[str, Dict[str, Any]]:
    """Obtener kill chains predefinidos"""
    return {
        'apt29_cozy_bear': {
            'name': 'APT29 (Cozy Bear)',
            'description': 'Grupo ruso de espionaje, sofisticado y sigiloso',
            'techniques': ['T1566', 'T1059', 'T1055', 'T1003', 'T1021', 'T1041'],
            'severity': 'critical',
            'target': 'Government, Think Tanks'
        },
        'apt28_fancy_bear': {
            'name': 'APT28 (Fancy Bear)',
            'description': 'Grupo ruso, operaciones de inteligencia',
            'techniques': ['T1566', 'T1203', 'T1055', 'T1003', 'T1078', 'T1041'],
            'severity': 'critical',
            'target': 'Military, Government, Media'
        },
        'apt3_gothic_panda': {
            'name': 'APT3 (Gothic Panda)',
            'description': 'Grupo chino enfocado en espionaje',
            'techniques': ['T1190', 'T1059', 'T1136', 'T1087', 'T1021', 'T1048'],
            'severity': 'high',
            'target': 'Aerospace, Technology'
        },
        'ransomware_generic': {
            'name': 'Ransomware Generic Kill Chain',
            'description': 'Cadena típica de ransomware moderno',
            'techniques': ['T1566', 'T1059', 'T1562', 'T1003', 'T1083', 'T1486', 'T1490'],
            'severity': 'critical',
            'target': 'All sectors'
        },
        'credential_theft': {
            'name': 'Credential Theft Campaign',
            'description': 'Enfocado en robo de credenciales',
            'techniques': ['T1133', 'T1110', 'T1003', 'T1056', 'T1078', 'T1041'],
            'severity': 'high',
            'target': 'Corporate networks'
        }
    }


