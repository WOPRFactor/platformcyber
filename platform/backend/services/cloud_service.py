"""
Cloud Pentesting Service
=========================

Servicio completo para pentesting en entornos cloud (AWS, Azure, GCP).

Herramientas integradas:
- Pacu (AWS pentesting framework)
- ScoutSuite (Multi-cloud security audit)
- Prowler (AWS, Azure, GCP security)
- AzureHound (Azure AD enumeration)
- ROADtools (Azure AD analysis)
"""

import subprocess
import logging
import json
import threading
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from utils.validators import CommandSanitizer
from utils.parsers.cloud_parser import (
    PacuParser, ScoutSuiteParser, ProwlerParser,
    AzureHoundParser, ROADtoolsParser, CloudEnumParser
)
from utils.workspace_logger import log_to_workspace
from repositories import ScanRepository
from models import db

logger = logging.getLogger(__name__)


class CloudService:
    """Servicio completo para pentesting en Cloud."""
    
    def __init__(self, scan_repository: ScanRepository = None):
        """Inicializa el servicio."""
        self.scan_repo = scan_repository or ScanRepository()
        # output_dir se obtiene dinámicamente por workspace
        # Mantener fallback para compatibilidad (usar tmp del proyecto)
        from utils.workspace_filesystem import PROJECT_TMP_DIR
        self.output_dir = PROJECT_TMP_DIR / 'cloud_scans'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Parsers
        self.pacu_parser = PacuParser()
        self.scoutsuite_parser = ScoutSuiteParser()
        self.prowler_parser = ProwlerParser()
        self.azurehound_parser = AzureHoundParser()
        self.roadtools_parser = ROADtoolsParser()
        self.cloudenum_parser = CloudEnumParser()
    
    def _get_workspace_output_dir(self, scan_id: int) -> Path:
        """
        Obtiene directorio de output del workspace para un scan.
        
        Args:
            scan_id: ID del scan
        
        Returns:
            Path al directorio de output del workspace
        """
        from utils.workspace_filesystem import get_workspace_output_dir_from_scan
        return get_workspace_output_dir_from_scan(scan_id, 'cloud_scans')
    
    # ============================================
    # PACU (AWS Pentesting Framework)
    # ============================================
    
    def start_pacu_module(
        self,
        module_name: str,
        workspace_id: int,
        user_id: int,
        aws_profile: Optional[str] = None,
        module_args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta un módulo de Pacu.
        
        Args:
            module_name: Nombre del módulo (ej: 'iam__enum_permissions')
            workspace_id: ID del workspace
            user_id: ID del usuario
            aws_profile: Perfil AWS a usar (opcional)
            module_args: Argumentos para el módulo
        """
        scan = self.scan_repo.create(
            scan_type='cloud_pentesting',
            target=f'aws:{aws_profile or "default"}',
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'pacu',
                'provider': 'aws',
                'module': module_name,
                'profile': aws_profile
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = str(workspace_output_dir / f'pacu_{scan.id}.txt')
            
            # Pacu usa un formato especial de comandos
            # pacu --session session_name --exec "run module_name --args"
            command = [
                'pacu',
                '--session', f'scan_{scan.id}',
                '--exec', f'run {module_name}'
            ]
            
            if aws_profile:
                command.extend(['--profile', aws_profile])
            
            if module_args:
                args_str = ' '.join([f'--{k} {v}' for k, v in module_args.items()])
                command[-1] += f' {args_str}'
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            # Log inicial
            log_to_workspace(
                workspace_id=workspace_id,
                source='PACU',
                level='INFO',
                message=f"Iniciando Pacu: módulo {module_name}",
                metadata={'scan_id': scan.id, 'module': module_name, 'provider': 'aws', 'command': ' '.join(sanitized_cmd)}
            )
            
            logger.info(f"Starting Pacu module {module_name} - scan {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'pacu', module_name, workspace_id)
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'pacu',
                'module': module_name,
                'provider': 'aws'
            }
            
        except Exception as e:
            logger.error(f"Error starting Pacu: {e}")
            log_to_workspace(
                workspace_id=workspace_id,
                source='PACU',
                level='ERROR',
                message=f"Error iniciando Pacu: {str(e)}",
                metadata={'scan_id': scan.id, 'module': module_name, 'error': str(e)}
            )
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    # ============================================
    # SCOUTSUITE (Multi-cloud Security Audit)
    # ============================================
    
    def start_scoutsuite_scan(
        self,
        provider: str,
        workspace_id: int,
        user_id: int,
        profile: Optional[str] = None,
        regions: Optional[List[str]] = None,
        services: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta ScoutSuite para auditoría de seguridad.
        
        Args:
            provider: Proveedor cloud (aws, azure, gcp, alibaba, oci)
            workspace_id: ID del workspace
            user_id: ID del usuario
            profile: Perfil de credenciales
            regions: Regiones a escanear
            services: Servicios específicos a auditar
        """
        scan = self.scan_repo.create(
            scan_type='cloud_pentesting',
            target=f'{provider}:{profile or "default"}',
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'scoutsuite',
                'provider': provider,
                'profile': profile,
                'regions': regions,
                'services': services
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_dir = str(workspace_output_dir / f'scoutsuite_{scan.id}')
            Path(output_dir).mkdir(exist_ok=True)
            
            command = [
                'scout',
                provider,
                '--report-dir', output_dir,
                '--no-browser'
            ]
            
            if profile:
                command.extend(['--profile', profile])
            
            if regions:
                command.extend(['--regions', ','.join(regions)])
            
            if services:
                command.extend(['--services', ','.join(services)])
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            # Log inicial
            log_to_workspace(
                workspace_id=workspace_id,
                source='SCOUTSUITE',
                level='INFO',
                message=f"Iniciando ScoutSuite: {provider}",
                metadata={'scan_id': scan.id, 'provider': provider, 'command': ' '.join(sanitized_cmd)}
            )
            
            logger.info(f"Starting ScoutSuite scan {scan.id} for {provider}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_dir, 'scoutsuite', provider, workspace_id)
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'scoutsuite',
                'provider': provider
            }
            
        except Exception as e:
            logger.error(f"Error starting ScoutSuite: {e}")
            log_to_workspace(
                workspace_id=workspace_id,
                source='SCOUTSUITE',
                level='ERROR',
                message=f"Error iniciando ScoutSuite: {str(e)}",
                metadata={'scan_id': scan.id, 'provider': provider, 'error': str(e)}
            )
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    # ============================================
    # PROWLER (AWS, Azure, GCP Security)
    # ============================================
    
    def start_prowler_scan(
        self,
        provider: str,
        workspace_id: int,
        user_id: int,
        profile: Optional[str] = None,
        severity: Optional[List[str]] = None,
        compliance: Optional[str] = None,
        services: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta Prowler para auditoría de seguridad.
        
        Args:
            provider: Proveedor (aws, azure, gcp)
            workspace_id: ID del workspace
            user_id: ID del usuario
            profile: Perfil de credenciales
            severity: Severidades a incluir (critical, high, medium, low)
            compliance: Framework de compliance (cis, hipaa, gdpr, etc.)
            services: Servicios específicos
        """
        scan = self.scan_repo.create(
            scan_type='cloud_pentesting',
            target=f'{provider}:{profile or "default"}',
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'prowler',
                'provider': provider,
                'profile': profile,
                'severity': severity,
                'compliance': compliance
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_dir = str(workspace_output_dir / f'prowler_{scan.id}')
            Path(output_dir).mkdir(exist_ok=True)
            output_file = str(Path(output_dir) / 'prowler_output.json')
            
            command = [
                'prowler',
                provider,
                '--output-directory', output_dir,
                '--output-formats', 'json',
                '--no-banner'
            ]
            
            if profile:
                if provider == 'aws':
                    command.extend(['--profile', profile])
                elif provider == 'azure':
                    command.extend(['--sp-env-auth'])  # Service Principal
            
            if severity:
                command.extend(['--severity', ','.join(severity)])
            
            if compliance:
                command.extend(['--compliance', compliance])
            
            if services:
                command.extend(['--services', ','.join(services)])
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            # Log inicial
            log_to_workspace(
                workspace_id=workspace_id,
                source='PROWLER',
                level='INFO',
                message=f"Iniciando Prowler: {provider}",
                metadata={'scan_id': scan.id, 'provider': provider, 'command': ' '.join(sanitized_cmd)}
            )
            
            logger.info(f"Starting Prowler scan {scan.id} for {provider}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'prowler', provider, workspace_id)
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'prowler',
                'provider': provider
            }
            
        except Exception as e:
            logger.error(f"Error starting Prowler: {e}")
            log_to_workspace(
                workspace_id=workspace_id,
                source='PROWLER',
                level='ERROR',
                message=f"Error iniciando Prowler: {str(e)}",
                metadata={'scan_id': scan.id, 'provider': provider, 'error': str(e)}
            )
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    # ============================================
    # AZUREHOUND (Azure AD Enumeration)
    # ============================================
    
    def start_azurehound_collection(
        self,
        tenant_id: str,
        workspace_id: int,
        user_id: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        access_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta AzureHound para enumerar Azure AD.
        
        Args:
            tenant_id: ID del tenant de Azure
            workspace_id: ID del workspace
            user_id: ID del usuario
            username: Usuario de Azure AD
            password: Password
            access_token: Token de acceso (alternativa a user/pass)
        """
        scan = self.scan_repo.create(
            scan_type='cloud_pentesting',
            target=f'azure:{tenant_id}',
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'azurehound',
                'provider': 'azure',
                'tenant_id': tenant_id
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            output_file = str(workspace_output_dir / f'azurehound_{scan.id}.json')
            
            command = [
                'azurehound',
                '-t', tenant_id,
                '-o', output_file
            ]
            
            if access_token:
                command.extend(['--access-token', access_token])
            elif username and password:
                command.extend(['-u', username, '-p', password])
            else:
                # Usar device code auth
                command.append('--use-device-code')
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            # Log inicial
            log_to_workspace(
                workspace_id=workspace_id,
                source='AZUREHOUND',
                level='INFO',
                message=f"Iniciando AzureHound: tenant {tenant_id}",
                metadata={'scan_id': scan.id, 'tenant_id': tenant_id, 'command': ' '.join(sanitized_cmd)}
            )
            
            logger.info(f"Starting AzureHound collection {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, output_file, 'azurehound', tenant_id, workspace_id)
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'azurehound',
                'provider': 'azure',
                'tenant_id': tenant_id
            }
            
        except Exception as e:
            logger.error(f"Error starting AzureHound: {e}")
            log_to_workspace(
                workspace_id=workspace_id,
                source='AZUREHOUND',
                level='ERROR',
                message=f"Error iniciando AzureHound: {str(e)}",
                metadata={'scan_id': scan.id, 'tenant_id': tenant_id, 'error': str(e)}
            )
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    # ============================================
    # ROADTOOLS (Azure AD Analysis)
    # ============================================
    
    def start_roadrecon_gather(
        self,
        workspace_id: int,
        user_id: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        access_token: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta roadrecon para recopilar datos de Azure AD.
        
        Args:
            workspace_id: ID del workspace
            user_id: ID del usuario
            username: Usuario de Azure AD
            password: Password
            access_token: Token de acceso
            tenant_id: ID del tenant (opcional)
        """
        scan = self.scan_repo.create(
            scan_type='cloud_pentesting',
            target=f'azure:{tenant_id or "default"}',
            workspace_id=workspace_id,
            user_id=user_id,
            options={
                'tool': 'roadtools',
                'provider': 'azure',
                'action': 'gather'
            }
        )
        
        try:
            workspace_output_dir = self._get_workspace_output_dir(scan.id)
            db_path = str(workspace_output_dir / f'roadtools_{scan.id}.db')
            
            command = ['roadrecon', 'gather', '--database', db_path]
            
            if access_token:
                command.extend(['--access-token', access_token])
            elif username and password:
                command.extend(['--username', username, '--password', password])
                if tenant_id:
                    command.extend(['--tenant-id', tenant_id])
            else:
                # Usar device code auth
                command.append('--device-code')
            
            sanitized_cmd = CommandSanitizer.sanitize_command(command[0], command[1:])
            
            # Log inicial
            log_to_workspace(
                workspace_id=workspace_id,
                source='ROADTOOLS',
                level='INFO',
                message=f"Iniciando ROADtools: gather",
                metadata={'scan_id': scan.id, 'action': 'gather', 'command': ' '.join(sanitized_cmd)}
            )
            
            logger.info(f"Starting ROADtools gather {scan.id}")
            
            thread = threading.Thread(
                target=self._execute_scan,
                args=(scan.id, sanitized_cmd, db_path, 'roadtools', 'gather', workspace_id)
            )
            thread.daemon = True
            thread.start()
            
            self.scan_repo.update_status(scan, 'running')
            
            return {
                'scan_id': scan.id,
                'status': 'running',
                'tool': 'roadtools',
                'provider': 'azure',
                'action': 'gather'
            }
            
        except Exception as e:
            logger.error(f"Error starting ROADtools: {e}")
            log_to_workspace(
                workspace_id=workspace_id,
                source='ROADTOOLS',
                level='ERROR',
                message=f"Error iniciando ROADtools: {str(e)}",
                metadata={'scan_id': scan.id, 'action': 'gather', 'error': str(e)}
            )
            self.scan_repo.update_status(scan, 'failed', str(e))
            raise
    
    # ============================================
    # PREVIEW METHODS
    # ============================================
    
    def preview_pacu_module(
        self,
        module_name: str,
        workspace_id: int,
        aws_profile: Optional[str] = None,
        module_args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Preview del comando Pacu."""
        command = [
            'pacu',
            '--session', f'scan_{{scan_id}}',
            '--exec', f'run {module_name}'
        ]
        
        if aws_profile:
            command.extend(['--profile', aws_profile])
        
        if module_args:
            args_str = ' '.join([f'--{k} {v}' for k, v in module_args.items()])
            command[-1] += f' {args_str}'
        
        command_str = ' '.join(command)
        output_file = f'/workspaces/workspace_{workspace_id}/cloud_scans/pacu_{{scan_id}}.txt'
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'module': module_name,
                'provider': 'aws',
                'profile': aws_profile,
                'module_args': module_args
            },
            'estimated_timeout': 1800,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_scoutsuite_scan(
        self,
        provider: str,
        workspace_id: int,
        profile: Optional[str] = None,
        regions: Optional[List[str]] = None,
        services: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Preview del comando ScoutSuite."""
        output_dir = f'/workspaces/workspace_{workspace_id}/cloud_scans/scoutsuite_{{scan_id}}'
        
        command = [
            'scout',
            provider,
            '--report-dir', output_dir,
            '--no-browser'
        ]
        
        if profile:
            command.extend(['--profile', profile])
        
        if regions:
            command.extend(['--regions', ','.join(regions)])
        
        if services:
            command.extend(['--services', ','.join(services)])
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'provider': provider,
                'profile': profile,
                'regions': regions,
                'services': services
            },
            'estimated_timeout': 3600,
            'output_file': output_dir,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_prowler_scan(
        self,
        provider: str,
        workspace_id: int,
        profile: Optional[str] = None,
        severity: Optional[List[str]] = None,
        compliance: Optional[str] = None,
        services: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Preview del comando Prowler."""
        output_dir = f'/workspaces/workspace_{workspace_id}/cloud_scans/prowler_{{scan_id}}'
        
        command = [
            'prowler',
            provider,
            '--output-directory', output_dir,
            '--output-formats', 'json',
            '--no-banner'
        ]
        
        if profile:
            if provider == 'aws':
                command.extend(['--profile', profile])
            elif provider == 'azure':
                command.extend(['--sp-env-auth'])
        
        if severity:
            command.extend(['--severity', ','.join(severity)])
        
        if compliance:
            command.extend(['--compliance', compliance])
        
        if services:
            command.extend(['--services', ','.join(services)])
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'provider': provider,
                'profile': profile,
                'severity': severity,
                'compliance': compliance,
                'services': services
            },
            'estimated_timeout': 3600,
            'output_file': f'{output_dir}/prowler_output.json',
            'warnings': [],
            'suggestions': []
        }
    
    def preview_azurehound_collection(
        self,
        tenant_id: str,
        workspace_id: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        access_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando AzureHound."""
        output_file = f'/workspaces/workspace_{workspace_id}/cloud_scans/azurehound_{{scan_id}}.json'
        
        command = [
            'azurehound',
            '-t', tenant_id,
            '-o', output_file
        ]
        
        if access_token:
            command.extend(['--access-token', '***'])
        elif username and password:
            command.extend(['-u', username, '-p', '***'])
        else:
            command.append('--use-device-code')
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'tenant_id': tenant_id,
                'username': username,
                'password': '***' if password else None,
                'access_token': '***' if access_token else None
            },
            'estimated_timeout': 1800,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_roadrecon_gather(
        self,
        workspace_id: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        access_token: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando ROADtools."""
        db_path = f'/workspaces/workspace_{workspace_id}/cloud_scans/roadtools_{{scan_id}}.db'
        
        command = ['roadrecon', 'gather', '--database', db_path]
        
        if access_token:
            command.extend(['--access-token', '***'])
        elif username and password:
            command.extend(['--username', username, '--password', '***'])
            if tenant_id:
                command.extend(['--tenant-id', tenant_id])
        else:
            command.append('--device-code')
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'username': username,
                'password': '***' if password else None,
                'access_token': '***' if access_token else None,
                'tenant_id': tenant_id
            },
            'estimated_timeout': 1800,
            'output_file': db_path,
            'warnings': [],
            'suggestions': []
        }
    
    # ============================================
    # OBTENER RESULTADOS
    # ============================================
    
    def get_scan_results(self, scan_id: int) -> Dict[str, Any]:
        """Obtiene y parsea resultados de cloud scan."""
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
        provider = scan.options.get('provider')
        
        workspace_output_dir = self._get_workspace_output_dir(scan_id)
        
        try:
            if tool == 'pacu':
                output_file = workspace_output_dir / f'pacu_{scan_id}.txt'
                if output_file.exists():
                    with open(output_file, 'r') as f:
                        module_name = scan.options.get('module', 'unknown')
                        results = self.pacu_parser.parse_module_output(f.read(), module_name)
                else:
                    results = {'error': 'Pacu output file not found'}
            
            elif tool == 'scoutsuite':
                output_dir = workspace_output_dir / f'scoutsuite_{scan_id}'
                # ScoutSuite genera scoutsuite-report/scoutsuite-results/scoutsuite_results_*.js
                json_files = list(output_dir.glob('**/scoutsuite_results_*.js'))
                if json_files:
                    # Convertir .js a JSON válido
                    with open(json_files[0], 'r') as f:
                        content = f.read()
                        json_start = content.find('{')
                        json_content = content[json_start:].rstrip(';')
                        temp_json = workspace_output_dir / f'scoutsuite_{scan_id}_temp.json'
                        with open(temp_json, 'w') as temp_f:
                            temp_f.write(json_content)
                        results = self.scoutsuite_parser.parse_json_report(str(temp_json))
                else:
                    results = {'message': 'Check HTML report in output directory'}
            
            elif tool == 'prowler':
                output_dir = workspace_output_dir / f'prowler_{scan_id}'
                json_files = list(output_dir.glob('*.json'))
                if json_files:
                    results = self.prowler_parser.parse_json_report(str(json_files[0]))
                else:
                    results = {'error': 'Prowler JSON report not found'}
            
            elif tool == 'azurehound':
                output_file = workspace_output_dir / f'azurehound_{scan_id}.json'
                if output_file.exists():
                    results = self.azurehound_parser.parse_json_output(str(output_file))
                else:
                    results = {'error': 'AzureHound output file not found'}
            
            elif tool == 'roadtools':
                db_path = workspace_output_dir / f'roadtools_{scan_id}.db'
                if Path(db_path).exists():
                    results = self.roadtools_parser.parse_database_summary(str(db_path))
                else:
                    results = {'error': 'ROADtools database not found'}
            
            else:
                results = {'error': f'Unknown tool: {tool}'}
            
            return {
                'scan_id': scan_id,
                'status': 'completed',
                'tool': tool,
                'provider': provider,
                'results': results,
                'scan_info': {
                    'target': scan.target,
                    'started_at': scan.started_at.isoformat() if scan.started_at else None,
                    'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing cloud scan results {scan_id}: {e}")
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
        tool: str,
        context: str,
        workspace_id: int
    ) -> None:
        """Ejecuta cloud scan en thread separado."""
        try:
            logger.info(f"Executing {tool} {scan_id}: {' '.join(command)}")
            
            # Timeouts largos para cloud scans
            timeout_map = {
                'pacu': 1800,        # 30 min
                'scoutsuite': 3600,  # 60 min
                'prowler': 3600,     # 60 min
                'azurehound': 1800,  # 30 min
                'roadtools': 1800    # 30 min
            }
            timeout = timeout_map.get(tool, 3600)
            
            # Environment con credenciales cloud
            env = CommandSanitizer.get_safe_env()
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            
            # Guardar output
            if result.stdout and not Path(output_file).exists():
                Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w') as f:
                    f.write(result.stdout)
            
            scan = self.scan_repo.find_by_id(scan_id)
            
            if result.returncode == 0:
                self.scan_repo.update_status(scan, 'completed')
                self.scan_repo.update_progress(scan, 100, result.stdout[:1000])
                logger.info(f"{tool} {scan_id} completed")
                
                # Log de éxito
                log_to_workspace(
                    workspace_id=workspace_id,
                    source=tool.upper(),
                    level='INFO',
                    message=f"{tool} completado exitosamente",
                    metadata={'scan_id': scan_id, 'status': 'completed'}
                )
            else:
                error_msg = result.stderr or "Unknown error"
                self.scan_repo.update_status(scan, 'failed', error_msg)
                logger.error(f"{tool} {scan_id} failed: {error_msg}")
                
                # Log de error
                log_to_workspace(
                    workspace_id=workspace_id,
                    source=tool.upper(),
                    level='ERROR',
                    message=f"{tool} falló: {error_msg}",
                    metadata={'scan_id': scan_id, 'status': 'failed', 'error': error_msg}
                )
                
        except subprocess.TimeoutExpired:
            scan = self.scan_repo.find_by_id(scan_id)
            self.scan_repo.update_status(scan, 'failed', f'Timeout ({timeout}s)')
            logger.error(f"{tool} {scan_id} timeout")
            
            # Log de timeout
            log_to_workspace(
                workspace_id=workspace_id,
                source=tool.upper(),
                level='ERROR',
                message=f"{tool} timeout después de {timeout}s",
                metadata={'scan_id': scan_id, 'status': 'failed', 'timeout': timeout}
            )
            
        except Exception as e:
            scan = self.scan_repo.find_by_id(scan_id)
            self.scan_repo.update_status(scan, 'failed', str(e))
            logger.error(f"{tool} {scan_id} error: {e}", exc_info=True)
            
            # Log de excepción
            log_to_workspace(
                workspace_id=workspace_id,
                source=tool.upper(),
                level='ERROR',
                message=f"{tool} error: {str(e)}",
                metadata={'scan_id': scan_id, 'status': 'failed', 'error': str(e)}
            )
