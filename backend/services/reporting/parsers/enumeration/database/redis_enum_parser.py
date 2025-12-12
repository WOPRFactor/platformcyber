"""
Parser para Redis Enumeration.
Formato: TXT con info de Redis (version, keys, memory).
"""

from pathlib import Path
from typing import List
import re
from ...base_parser import BaseParser, ParsedFinding


class RedisEnumParser(BaseParser):
    """Parser para archivos de Redis enumeration."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return 'redis' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de Redis enumeration.
        
        Formato:
        Redis version: 6.2.6
        Keys: 100
        Memory: 1048576 bytes
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            redis_version = None
            key_count = 0
            memory_bytes = 0
            
            for line in lines:
                line_stripped = line.strip()
                
                # Extraer versión
                if 'Redis version:' in line:
                    match = re.search(r'(\d+\.\d+\.\d+)', line)
                    if match:
                        redis_version = match.group(1)
                
                # Extraer key count
                elif 'Keys:' in line:
                    match = re.search(r'Keys:\s+(\d+)', line)
                    if match:
                        key_count = int(match.group(1))
                
                # Extraer memory
                elif 'Memory:' in line:
                    match = re.search(r'Memory:\s+(\d+)', line)
                    if match:
                        memory_bytes = int(match.group(1))
            
            # Finding para Redis accesible
            if redis_version or key_count > 0:
                severity = 'high' if key_count > 0 else 'medium'
                
                finding = ParsedFinding(
                    title=f"Redis instance accessible",
                    severity=severity,
                    description=f"Redis {redis_version or 'unknown version'} accessible with {key_count} keys",
                    category='database_misconfiguration',
                    affected_target='redis_server',
                    evidence=f"Version: {redis_version}, Keys: {key_count}, Memory: {memory_bytes} bytes",
                    remediation="Enable Redis authentication (requirepass) and bind to localhost only",
                    raw_data={
                        'tool': 'redis_enum',
                        'version': redis_version,
                        'key_count': key_count,
                        'memory_bytes': memory_bytes
                    }
                )
                findings.append(finding)
            
            self.logger.info(f"Redis Enum: Parsed Redis instance with {key_count} keys")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing Redis enum file {file_path}: {e}")
            return findings
