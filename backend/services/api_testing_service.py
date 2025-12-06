"""
API Testing Service
===================

Servicio completo para pentesting de APIs REST, GraphQL, SOAP.

Herramientas integradas:
- Arjun (parameter discovery)
- Kiterunner (API route discovery)
- JWT_Tool (JWT analysis & manipulation)
- FFUF (web fuzzing)
- Wfuzz (web fuzzing)
- GraphQL introspection
- Postman/Newman (API testing automation)
"""

import subprocess
import logging
import json
import threading
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from utils.validators import CommandSanitizer, DomainValidator
from utils.parsers.api_parser import (
    ArjunParser, KiterunnerParser, JWTToolParser,
    FFUFParser, WfuzzParser, GraphQLParser, PostmanParser
)
from repositories import ScanRepository

logger = logging.getLogger(__name__)


class APITestingService:
    """Servicio completo para API pentesting."""
    
    def __init__(self, scan_repository: ScanRepository = None):
        """Inicializa el servicio."""
        self.scan_repo = scan_repository or ScanRepository()
        from utils.workspace_filesystem import PROJECT_TMP_DIR
        self.output_dir = PROJECT_TMP_DIR / 'api_testing'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Parsers
        self.arjun_parser = ArjunParser()
        self.kiterunner_parser = KiterunnerParser()
        self.jwt_parser = JWTToolParser()
        self.ffuf_parser = FFUFParser()
        self.wfuzz_parser = WfuzzParser()
        self.graphql_parser = GraphQLParser()
        self.postman_parser = PostmanParser()
    
    # ============================================
    # ARJUN (Parameter Discovery)
    # ============================================
    
    def start_arjun_scan(
        self,
        url: str,
        workspace_id: int,
        user_id: int,
        methods: Optional[List[str]] = None,
        wordlist: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta Arjun para descubrir parámetros.
        
        Args:
            url: URL objetivo
            workspace_id: ID del workspace
            user_id: ID del usuario
            methods: Métodos HTTP a probar (GET, POST, JSON)
            wordlist: Wordlist personalizada (opcional)
        """
        DomainValidator.is_valid_domain(url.split('//')[1].split('/')[0])
        
        scan = self.scan_repo.create(
            scan_type='api_testing',
            target=url,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'arjun',
                'methods': methods or ['GET', 'POST']
            }
        )
        
        try:
            output_file = str(self.output_dir / f'arjun_{scan.id}.txt')
            
            command = ['arjun', '-u', url, '-o', output_file]
            
            if methods:
                command.extend(['-m', ','.join(methods)])
            
            if wordlist:
                command.extend(['-w', wordlist])
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting Arjun scan {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'arjun')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'arjun',
                'target': url
            }
            
        except Exception as e:
            logger.error(f"Error starting Arjun: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    # ============================================
    # KITERUNNER (API Route Discovery)
    # ============================================
    
    def start_kiterunner_scan(
        self,
        url: str,
        workspace_id: int,
        user_id: int,
        wordlist: Optional[str] = None,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Ejecuta Kiterunner para descubrir rutas de API.
        
        Args:
            url: URL base del API
            workspace_id: ID del workspace
            user_id: ID del usuario
            wordlist: Wordlist de rutas (opcional)
            max_depth: Profundidad máxima de búsqueda
        """
        DomainValidator.is_valid_domain(url.split('//')[1].split('/')[0])
        
        scan = self.scan_repo.create(
            scan_type='api_testing',
            target=url,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'kiterunner',
                'max_depth': max_depth
            }
        )
        
        try:
            output_file = str(self.output_dir / f'kiterunner_{scan.id}.txt')
            
            command = ['kr', 'scan', url, '-o', output_file]
            
            if wordlist:
                command.extend(['-w', wordlist])
            else:
                # Usar wordlist por defecto de kiterunner
                command.extend(['-w', 'routes-large.kite'])
            
            command.extend(['--max-depth', str(max_depth)])
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting Kiterunner scan {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'kiterunner')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'kiterunner',
                'target': url
            }
            
        except Exception as e:
            logger.error(f"Error starting Kiterunner: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    # ============================================
    # JWT_TOOL (JWT Analysis)
    # ============================================
    
    def analyze_jwt(
        self,
        jwt_token: str,
        workspace_id: int,
        user_id: int,
        crack_secret: bool = False
    ) -> Dict[str, Any]:
        """
        Analiza un JWT token.
        
        Args:
            jwt_token: El JWT token a analizar
            workspace_id: ID del workspace
            user_id: ID del usuario
            crack_secret: Intentar crackear el secret
        """
        scan = self.scan_repo.create(
            scan_type='api_testing',
            target='JWT Token Analysis',
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'jwt_tool',
                'crack_secret': crack_secret
            }
        )
        
        try:
            output_file = str(self.output_dir / f'jwt_{scan.id}.txt')
            
            # Guardar JWT en archivo temporal
            jwt_file = self.output_dir / f'jwt_{scan.id}_input.txt'
            with open(jwt_file, 'w') as f:
                f.write(jwt_token)
            
            command = ['jwt_tool', str(jwt_file)]
            
            if crack_secret:
                command.extend(['-C', '-d', '/usr/share/wordlists/rockyou.txt'])
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting JWT analysis {scan.id}")
            
            # Ejecutar sync (rápido)
            result = subprocess.run(
                sanitized_cmd,
                capture_output=True,
                text=True,
                timeout=300,
                env=CommandSanitizer.get_safe_env()
            )
            
            with open(output_file, 'w') as f:
                f.write(result.stdout)
            
            if result.returncode == 0:
                self.scan_repo.update_status(scan, 'completed')
                self.scan_repo.update_progress(scan, 100, 'JWT analysis completed')
            else:
                self.scan_repo.update_status(scan, 'failed', result.stderr)
            
            return {
                'scan_id': scan.id,
                'status': 'completed',
                'tool': 'jwt_tool',
                'results': self.jwt_parser.parse_jwt_info(result.stdout)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing JWT: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    # ============================================
    # FFUF (Web Fuzzing)
    # ============================================
    
    def start_ffuf_scan(
        self,
        url: str,
        workspace_id: int,
        user_id: int,
        wordlist: str,
        fuzz_param: str = 'FUZZ',
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta FFUF para fuzzing.
        
        Args:
            url: URL con marcador FUZZ (ej: http://example.com/FUZZ)
            workspace_id: ID del workspace
            user_id: ID del usuario
            wordlist: Path al wordlist
            fuzz_param: Marcador a reemplazar (default: FUZZ)
            filters: Filtros (status codes, size, etc.)
        """
        DomainValidator.is_valid_domain(url.split('//')[1].split('/')[0])
        
        scan = self.scan_repo.create(
            scan_type='api_testing',
            target=url,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'ffuf',
                'fuzz_param': fuzz_param,
                'filters': filters or {}
            }
        )
        
        try:
            output_file = str(self.output_dir / f'ffuf_{scan.id}.json')
            
            command = [
                'ffuf',
                '-u', url,
                '-w', wordlist,
                '-o', output_file,
                '-of', 'json',
                '-t', '50'  # 50 threads
            ]
            
            # Aplicar filtros
            if filters:
                if 'status_codes' in filters:
                    command.extend(['-mc', ','.join(map(str, filters['status_codes']))])
                if 'size' in filters:
                    command.extend(['-fs', str(filters['size'])])
                if 'words' in filters:
                    command.extend(['-fw', str(filters['words'])])
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            logger.info(f"Starting FFUF scan {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'ffuf')
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'ffuf',
                'target': url
            }
            
        except Exception as e:
            logger.error(f"Error starting FFUF: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    # ============================================
    # GRAPHQL (Introspection)
    # ============================================
    
    def graphql_introspect(
        self,
        url: str,
        workspace_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Ejecuta introspection de GraphQL.
        
        Args:
            url: URL del endpoint GraphQL
            workspace_id: ID del workspace
            user_id: ID del usuario
        """
        scan = self.scan_repo.create(
            scan_type='api_testing',
            target=url,
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'graphql',
                'action': 'introspection'
            }
        )
        
        try:
            # Query de introspection estándar
            introspection_query = """
            query IntrospectionQuery {
                __schema {
                    queryType { name }
                    mutationType { name }
                    subscriptionType { name }
                    types {
                        ...FullType
                    }
                }
            }
            fragment FullType on __Type {
                kind
                name
                fields {
                    name
                    args {
                        ...InputValue
                    }
                    type {
                        ...TypeRef
                    }
                }
            }
            fragment InputValue on __InputValue {
                name
                type { ...TypeRef }
                defaultValue
            }
            fragment TypeRef on __Type {
                kind
                name
                ofType {
                    kind
                    name
                    ofType {
                        kind
                        name
                    }
                }
            }
            """
            
            # Ejecutar con curl
            command = [
                'curl', '-X', 'POST',
                url,
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({'query': introspection_query})
            ]
            
            logger.info(f"Starting GraphQL introspection {scan.id}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
                env=CommandSanitizer.get_safe_env()
            )
            
            output_file = self.output_dir / f'graphql_{scan.id}.json'
            with open(output_file, 'w') as f:
                f.write(result.stdout)
            
            if result.returncode == 0:
                self.scan_repo.update_status(scan, 'completed')
                results = self.graphql_parser.parse_introspection(result.stdout)
            else:
                self.scan_repo.update_status(scan, 'failed', result.stderr)
                results = {'error': result.stderr}
            
            return {
                'scan_id': scan.id,
                'status': 'completed',
                'tool': 'graphql',
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error in GraphQL introspection: {e}")
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    # ============================================
    # OBTENER RESULTADOS
    # ============================================
    
    def get_scan_results(self, scan_id: int) -> Dict[str, Any]:
        """Obtiene y parsea resultados de API testing scan."""
        scan = self.scan_repo.find_by_id(scan_id)
        
        if not scan:
            raise ValueError(f'Scan {scan_id} not found')
        
        if scan.status != 'completed':
            return {
                'scan_id': scan_id,
                'status': scan.status,
                'message': 'Scan not completed yet'
            }
        
        tool = scan.options.get('tool')
        
        try:
            if tool == 'arjun':
                output_file = self.output_dir / f'arjun_{scan_id}.txt'
                with open(output_file, 'r') as f:
                    results = self.arjun_parser.parse_output(f.read())
            
            elif tool == 'kiterunner':
                output_file = self.output_dir / f'kiterunner_{scan_id}.txt'
                with open(output_file, 'r') as f:
                    results = self.kiterunner_parser.parse_output(f.read())
            
            elif tool == 'jwt_tool':
                output_file = self.output_dir / f'jwt_{scan_id}.txt'
                with open(output_file, 'r') as f:
                    results = self.jwt_parser.parse_jwt_info(f.read())
            
            elif tool == 'ffuf':
                output_file = self.output_dir / f'ffuf_{scan_id}.json'
                with open(output_file, 'r') as f:
                    results = self.ffuf_parser.parse_json(f.read())
            
            elif tool == 'graphql':
                output_file = self.output_dir / f'graphql_{scan_id}.json'
                with open(output_file, 'r') as f:
                    results = self.graphql_parser.parse_introspection(f.read())
            
            else:
                results = {'error': f'Unknown tool: {tool}'}
            
            return {
                'scan_id': scan_id,
                'status': 'completed',
                'tool': tool,
                'results': results,
                'scan_info': {
                    'target': scan.target,
                    'started_at': scan.started_at.isoformat() if scan.started_at else None,
                    'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing API testing results {scan_id}: {e}")
            return {
                'scan_id': scan_id,
                'error': f'Failed to parse results: {str(e)}'
            }
    
    # ============================================
    # HELPERS PRIVADOS
    # ============================================
    
    def _execute_scan(
        self,
        scan_id: int,
        command: list,
        output_file: str,
        tool: str
    ) -> None:
        """Ejecuta API testing scan en thread separado."""
        try:
            logger.info(f"Executing {tool} {scan_id}: {' '.join(command)}")
            
            # Timeouts
            timeout_map = {
                'arjun': 600,       # 10 min
                'kiterunner': 900,  # 15 min
                'ffuf': 600,        # 10 min
                'wfuzz': 600        # 10 min
            }
            timeout = timeout_map.get(tool, 600)
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=CommandSanitizer.get_safe_env()
            )
            
            # Guardar output si no existe
            if not Path(output_file).exists() and result.stdout:
                with open(output_file, 'w') as f:
                    f.write(result.stdout)
            
            scan = self.scan_repo.find_by_id(scan_id)
            
            if result.returncode == 0:
                self.scan_repo.update_status(scan, 'completed')
                self.scan_repo.update_progress(scan, 100, result.stdout[:1000])
                logger.info(f"{tool} {scan_id} completed")
            else:
                error_msg = result.stderr or "Unknown error"
                self.scan_repo.update_status(scan, 'failed', error_msg)
                logger.error(f"{tool} {scan_id} failed: {error_msg}")
                
        except subprocess.TimeoutExpired:
            scan = self.scan_repo.find_by_id(scan_id)
            self.scan_repo.update_status(scan, 'failed', f'Timeout ({timeout}s)')
            logger.error(f"{tool} {scan_id} timeout")
            
        except Exception as e:
            scan = self.scan_repo.find_by_id(scan_id)
            self.scan_repo.update_status(scan, 'failed', str(e))
            logger.error(f"{tool} {scan_id} error: {e}", exc_info=True)

