"""
Compliance Mapping Generator
=============================

Generador de mapeo de compliance.
"""

from typing import Dict, Any, List
from collections import defaultdict
from models import Vulnerability


def generate_compliance_mapping(
    vulns: List[Vulnerability]
) -> Dict[str, Any]:
    """Genera mapeo de vulnerabilidades a frameworks de compliance."""
    # Simplificado: basado en severidad y tipo
    compliance_map = {
        'OWASP_Top_10': defaultdict(list),
        'CIS_Controls': defaultdict(list),
        'NIST_CSF': defaultdict(list),
        'ISO_27001': defaultdict(list),
        'PCI_DSS': defaultdict(list)
    }
    
    for vuln in vulns:
        # Mapeo simplificado basado en título
        title_lower = vuln.title.lower()
        
        # OWASP Top 10
        if 'injection' in title_lower or 'sql' in title_lower:
            compliance_map['OWASP_Top_10']['A03:2021-Injection'].append(vuln.id)
        if 'xss' in title_lower or 'cross-site' in title_lower:
            compliance_map['OWASP_Top_10']['A03:2021-Injection'].append(vuln.id)
        if 'authentication' in title_lower or 'password' in title_lower:
            compliance_map['OWASP_Top_10']['A07:2021-Identification_and_Authentication_Failures'].append(vuln.id)
        if 'crypto' in title_lower or 'encryption' in title_lower or 'ssl' in title_lower:
            compliance_map['OWASP_Top_10']['A02:2021-Cryptographic_Failures'].append(vuln.id)
        
        # CIS Controls (simplificado)
        if vuln.severity in ['critical', 'high']:
            compliance_map['CIS_Controls']['Control_1_Inventory'].append(vuln.id)
            compliance_map['CIS_Controls']['Control_18_Application_Software_Security'].append(vuln.id)
    
    # Convertir defaultdict a dict normal y contar
    result = {}
    for framework, mappings in compliance_map.items():
        result[framework] = {
            control: {'count': len(vuln_ids), 'vulnerabilities': vuln_ids}
            for control, vuln_ids in mappings.items()
        }
    
    return result

