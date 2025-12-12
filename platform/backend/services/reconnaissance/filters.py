"""
Reconnaissance Output Filters
==============================

Funciones para filtrar warnings y mensajes informativos de herramientas de reconocimiento.
"""

from typing import Tuple


def filter_dnsenum_warnings(output: str) -> str:
    """
    Filtra warnings conocidos de dnsenum que no son errores reales.
    
    Args:
        output: Salida de texto que puede contener warnings de dnsenum
        
    Returns:
        Salida sin los warnings conocidos de AXFR
    """
    if not output:
        return output
    
    lines = output.split('\n')
    filtered_lines = []
    
    known_warnings = [
        'AXFR record query failed: FORMERR',
        'AXFR record query failed: NOTAUTH',
        'AXFR record query failed',
        'perhaps Google is blocking our queries',
        'Check manually'
    ]
    
    for line in lines:
        if any(warning in line for warning in known_warnings):
            continue
        
        if not line.strip():
            continue
        
        filtered_lines.append(line)
    
    return '\n'.join(filtered_lines).strip()


def filter_whois_informational_messages(output: str) -> Tuple[str, bool]:
    """
    Filtra mensajes informativos de whois que no son errores reales.
    
    Args:
        output: Salida de texto de whois
        
    Returns:
        Tupla (output_filtrado, es_informativo)
    """
    if not output:
        return output, False
    
    informational_patterns = [
        'this tld has no whois server',
        'but you can access the whois database at',
        'nic.uy',
        'nic.ar',
        'nic.br',
        'whois server not found',
        'no whois server',
        'registrar whois server',
    ]
    
    output_lower = output.lower()
    is_informational = any(pattern in output_lower for pattern in informational_patterns)
    
    if is_informational:
        useful_data_keywords = [
            'domain name:',
            'registrar:',
            'creation date:',
            'expiry date:',
            'name server:',
            'status:',
            'registrant:',
            'admin:',
            'tech:',
        ]
        
        has_useful_data = any(keyword in output_lower for keyword in useful_data_keywords)
        
        if not has_useful_data:
            return output, True
    
    return output, False


def filter_theharvester_banner(output: str) -> str:
    """
    Filtra el banner ASCII de theHarvester de la salida, preservando mensajes de error útiles.
    
    Args:
        output: Salida de texto que puede contener el banner
        
    Returns:
        Salida sin el banner, pero con mensajes de error preservados
    """
    if not output:
        return output
    
    lines = output.split('\n')
    filtered_lines = []
    in_banner = False
    
    for line in lines:
        stripped = line.strip()
        
        if 'Read proxies.yaml' in line:
            continue
        
        if '***' in stripped and len(stripped) > 10:
            asterisk_count = stripped.count('*')
            if asterisk_count >= 3:
                in_banner = True
                continue
        
        if in_banner:
            if '***' in stripped and len(stripped) > 10:
                asterisk_count = stripped.count('*')
                if asterisk_count >= 3:
                    in_banner = False
                continue
            
            if stripped.startswith('*'):
                continue
            
            if any(char in line for char in ['|', '_', '/', '\\']) and stripped.startswith('*'):
                continue
            
            if not stripped.startswith('*') and not any(char in line for char in ['|', '_', '/', '\\']):
                if len(stripped) > 0 and not stripped.startswith('*'):
                    in_banner = False
                else:
                    continue
        
        if stripped.startswith('*'):
            if stripped.count('*') >= 3:
                continue
            if any(char in line for char in ['|', '_', '/', '\\']):
                continue
        
        if any(keyword in line.lower() for keyword in ['theharvester', 'coded by', 'edge-security', 'cmartorella']):
            if stripped.startswith('*') or '***' in stripped:
                continue
        
        if stripped.replace('*', '').replace(' ', '').replace('\t', '') == '':
            continue
        
        filtered_lines.append(line)
    
    result = '\n'.join(filtered_lines).strip()
    return result


