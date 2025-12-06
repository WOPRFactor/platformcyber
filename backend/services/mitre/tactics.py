"""
MITRE ATT&CK Tactics Data
==========================

Datos de las 14 tácticas de MITRE ATT&CK Enterprise.
"""

from typing import Dict, Any


def get_tactics() -> Dict[str, Dict[str, Any]]:
    """Obtener todas las tácticas MITRE ATT&CK"""
    return {
        'TA0043': {
            'id': 'TA0043',
            'name': 'Reconnaissance',
            'description': 'Recopilación de información para planear operaciones futuras',
            'techniques_count': 10
        },
        'TA0042': {
            'id': 'TA0042',
            'name': 'Resource Development',
            'description': 'Establecer recursos para apoyar operaciones',
            'techniques_count': 7
        },
        'TA0001': {
            'id': 'TA0001',
            'name': 'Initial Access',
            'description': 'Obtener punto de entrada en la red',
            'techniques_count': 9
        },
        'TA0002': {
            'id': 'TA0002',
            'name': 'Execution',
            'description': 'Ejecutar código malicioso',
            'techniques_count': 12
        },
        'TA0003': {
            'id': 'TA0003',
            'name': 'Persistence',
            'description': 'Mantener acceso al sistema',
            'techniques_count': 19
        },
        'TA0004': {
            'id': 'TA0004',
            'name': 'Privilege Escalation',
            'description': 'Obtener permisos de nivel superior',
            'techniques_count': 13
        },
        'TA0005': {
            'id': 'TA0005',
            'name': 'Defense Evasion',
            'description': 'Evitar ser detectado',
            'techniques_count': 42
        },
        'TA0006': {
            'id': 'TA0006',
            'name': 'Credential Access',
            'description': 'Robar credenciales',
            'techniques_count': 17
        },
        'TA0007': {
            'id': 'TA0007',
            'name': 'Discovery',
            'description': 'Conocer el entorno',
            'techniques_count': 30
        },
        'TA0008': {
            'id': 'TA0008',
            'name': 'Lateral Movement',
            'description': 'Moverse a través de la red',
            'techniques_count': 9
        },
        'TA0009': {
            'id': 'TA0009',
            'name': 'Collection',
            'description': 'Recopilar datos de interés',
            'techniques_count': 17
        },
        'TA0011': {
            'id': 'TA0011',
            'name': 'Command and Control',
            'description': 'Comunicación con sistemas comprometidos',
            'techniques_count': 16
        },
        'TA0010': {
            'id': 'TA0010',
            'name': 'Exfiltration',
            'description': 'Robar datos',
            'techniques_count': 9
        },
        'TA0040': {
            'id': 'TA0040',
            'name': 'Impact',
            'description': 'Manipular, interrumpir o destruir sistemas',
            'techniques_count': 13
        }
    }


