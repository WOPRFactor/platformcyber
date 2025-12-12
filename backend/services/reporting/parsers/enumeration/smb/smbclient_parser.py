"""
Parser para SMBClient - SMB client tool.
Formato: TXT con output interactivo tipo 'ls'.
"""

from pathlib import Path
from typing import List
import re
from ...base_parser import BaseParser, ParsedFinding


class SMBClientParser(BaseParser):
    """Parser para archivos de SMBClient."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica si el archivo puede ser parseado."""
        filename = file_path.name.lower()
        return 'smbclient' in filename and file_path.suffix == '.txt'
    
    def parse(self, file_path: Path) -> List[ParsedFinding]:
        """
        Parsea archivo de SMBClient.
        
        Formato:
        smb: \\> ls
          file.txt       A     1024  Mon Jan  1 00:00:00 2024
          document.pdf   A    51200  Mon Jan  1 00:00:00 2024
        """
        findings = []
        
        try:
            content = self._read_file(file_path)
            if not content:
                return findings
            
            lines = content.split('\n')
            files_found = []
            
            for line in lines:
                line_stripped = line.strip()
                
                # Parsear líneas de archivos: filename  A  size  date
                # Formato:   file.txt       A     1024  Mon Jan  1 00:00:00 2024
                match = re.match(r'^([^\s]+)\s+(A|D)\s+(\d+)\s+(.+)', line_stripped)
                if match:
                    filename = match.group(1)
                    file_type = match.group(2)  # A=archivo, D=directorio
                    size = int(match.group(3))
                    date = match.group(4)
                    
                    # Ignorar directorios . y ..
                    if filename in ['.', '..']:
                        continue
                    
                    files_found.append({
                        'filename': filename,
                        'type': file_type,
                        'size': size,
                        'date': date
                    })
            
            # Crear un finding general si se encontraron archivos
            if files_found:
                file_count = len([f for f in files_found if f['type'] == 'A'])
                dir_count = len([f for f in files_found if f['type'] == 'D'])
                
                finding = ParsedFinding(
                    title=f"SMB Share contents enumerated",
                    severity='info',
                    description=f"Successfully enumerated share contents: {file_count} files, {dir_count} directories",
                    category='smb_enumeration',
                    affected_target='smb_share',
                    evidence=f"Files: {', '.join([f['filename'] for f in files_found[:5]])}{'...' if len(files_found) > 5 else ''}",
                    raw_data={
                        'tool': 'smbclient',
                        'file_count': file_count,
                        'directory_count': dir_count,
                        'files': files_found
                    }
                )
                findings.append(finding)
            
            self.logger.info(f"SMBClient: Parsed {len(files_found)} files/directories")
            return findings
            
        except Exception as e:
            self.logger.error(f"Error parsing SMBClient file {file_path}: {e}")
            return findings
