"""
Parser para DNS Zone Transfer (dig).
Formato: TXT con registros DNS estándar.
"""

from pathlib import Path
from typing import List
import re
from ...base_parser import BaseParser, ParsedFinding


class DNSZoneParser(BaseParser):
    """Parser para archivos de DNS zone transfer."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return ('dig' in filename or 'zone' in filename) and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de DNS zone transfer.
        
        Formato:
        example.com.  3600  IN  SOA  ns1.example.com. admin.example.com. (...)
        example.com.  3600  IN  A    192.168.1.1
        www.example.com. 3600 IN A   192.168.1.2
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            domain = None
            records = []
            
            for line in lines:
                line_stripped = line.strip()
                
                # Saltar comentarios
                if line_stripped.startswith(';'):
                    # Extraer dominio del header
                    if 'DiG' in line and 'AXFR' in line:
                        match = re.search(r'DiG.*?\s+([\w\.\-]+)\s+AXFR', line)
                        if match:
                            domain = match.group(1)
                    continue
                
                # Parsear registros DNS: DOMAIN  TTL  CLASS  TYPE  VALUE
                match = re.match(r'^([\w\.\-]+)\.\s+(\d+)\s+IN\s+(A|AAAA|CNAME|MX|NS|TXT|SOA)\s+(.+)', line_stripped)
                if match:
                    record_domain = match.group(1)
                    ttl = int(match.group(2))
                    record_type = match.group(3)
                    value = match.group(4)
                    
                    records.append({
                        'domain': record_domain,
                        'type': record_type,
                        'value': value,
                        'ttl': ttl
                    })
            
            # Finding general para zone transfer exitoso
            if records:
                finding = ParsedFinding(
                    title=f"DNS Zone Transfer successful",
                    severity='high',
                    description=f"DNS zone transfer allowed for domain {domain or 'unknown'} - {len(records)} records leaked",
                    category='dns_misconfiguration',
                    affected_target=domain or 'dns_server',
                    evidence=f"Records leaked: {len(records)} ({len([r for r in records if r['type'] == 'A'])} A, {len([r for r in records if r['type'] == 'MX'])} MX, {len([r for r in records if r['type'] == 'NS'])} NS)",
                    remediation="Restrict zone transfers (AXFR) to authorized secondary name servers only",
                    cve_id="CWE-284",
                    raw_data={
                        'tool': 'dig_zone_transfer',
                        'domain': domain,
                        'record_count': len(records),
                        'records': records[:50]  # Limitar a 50
                    }
                )
                findings.append(finding)
                
                # Findings adicionales por subdominios
                subdomains = [r['domain'] for r in records if r['type'] in ['A', 'AAAA', 'CNAME']]
                if subdomains:
                    finding = ParsedFinding(
                        title=f"Subdomains leaked via zone transfer",
                        severity='medium',
                        description=f"{len(subdomains)} subdomains discovered through DNS zone transfer",
                        category='information_disclosure',
                        affected_target=domain or 'dns_server',
                        evidence=f"Subdomains: {', '.join(subdomains[:10])}{'...' if len(subdomains) > 10 else ''}",
                        remediation="Restrict zone transfers to prevent information disclosure",
                        raw_data={
                            'tool': 'dig_zone_transfer',
                            'subdomains': subdomains
                        }
                    )
                    findings.append(finding)
            
            self.logger.info(f"DNS Zone Transfer: Parsed {len(records)} DNS records")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing DNS zone file {file_path}: {e}")
            return findings


