"""
Container Security Service
==========================

Servicio completo para pentesting de contenedores y Kubernetes.

Herramientas integradas:
- Trivy (Container vulnerability scanner)
- Grype (Vulnerability scanner for container images)
- Syft (SBOM generator)
- Kube-hunter (Kubernetes penetration testing)
- Kube-bench (CIS Kubernetes Benchmark)
- Kubescape (Kubernetes security platform)
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from utils.parsers.container_parser import (
    TrivyParser, GrypeParser, SyftParser,
    KubeHunterParser, KubeBenchParser, KubescapeParser
)
from utils.workspace_logger import log_to_workspace
from repositories import ScanRepository
from .base import BaseContainerService
from .tools import (
    TrivyScanner,
    GrypeScanner,
    SyftScanner,
    KubeHunterScanner,
    KubeBenchScanner,
    KubescapeScanner
)

logger = logging.getLogger(__name__)


class ContainerService(BaseContainerService):
    """Servicio completo para container & kubernetes security."""

    def __init__(self, scan_repository: ScanRepository = None):
        """Inicializa el servicio."""
        super().__init__(scan_repository)

        # Inicializar scanners individuales
        self.trivy = TrivyScanner(self.scan_repo)
        self.grype = GrypeScanner(self.scan_repo)
        self.syft = SyftScanner(self.scan_repo)
        self.kubehunter = KubeHunterScanner(self.scan_repo)
        self.kubebench = KubeBenchScanner(self.scan_repo)
        self.kubescape = KubescapeScanner(self.scan_repo)

        # Parsers para obtener resultados
        self.trivy_parser = TrivyParser()
        self.grype_parser = GrypeParser()
        self.syft_parser = SyftParser()
        self.kubehunter_parser = KubeHunterParser()
        self.kubebench_parser = KubeBenchParser()
        self.kubescape_parser = KubescapeParser()

    # ============================================
    # TRIVY (Container Vulnerability Scanner)
    # ============================================

    def scan_image_trivy(
        self,
        image: str,
        workspace_id: int,
        user_id: int,
        severity: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Escanea imagen Docker con Trivy."""
        result = self.trivy.scan_image(image, workspace_id, user_id, severity)
        
        # Log inicial
        log_to_workspace(
            workspace_id=workspace_id,
            source='TRIVY',
            level='INFO',
            message=f"Iniciando Trivy: escaneo de imagen {image}",
            metadata={'scan_id': result.get('scan_id'), 'image': image, 'severity': severity}
        )
        
        return result

    # ============================================
    # GRYPE (Vulnerability Scanner)
    # ============================================

    def scan_image_grype(
        self,
        image: str,
        workspace_id: int,
        user_id: int,
        scope: str = 'all-layers'
    ) -> Dict[str, Any]:
        """Escanea imagen con Grype."""
        result = self.grype.scan_image(image, workspace_id, user_id, scope)
        
        # Log inicial
        log_to_workspace(
            workspace_id=workspace_id,
            source='GRYPE',
            level='INFO',
            message=f"Iniciando Grype: escaneo de imagen {image}",
            metadata={'scan_id': result.get('scan_id'), 'image': image, 'scope': scope}
        )
        
        return result

    # ============================================
    # SYFT (SBOM Generator)
    # ============================================

    def generate_sbom(
        self,
        image: str,
        workspace_id: int,
        user_id: int,
        output_format: str = 'spdx-json'
    ) -> Dict[str, Any]:
        """Genera SBOM (Software Bill of Materials) con Syft."""
        result = self.syft.generate_sbom(image, workspace_id, user_id, output_format)
        
        # Log inicial
        log_to_workspace(
            workspace_id=workspace_id,
            source='SYFT',
            level='INFO',
            message=f"Iniciando Syft: generación de SBOM para {image}",
            metadata={'scan_id': result.get('scan_id'), 'image': image, 'format': output_format}
        )
        
        return result

    # ============================================
    # KUBE-HUNTER (Kubernetes Penetration Testing)
    # ============================================

    def run_kubehunter(
        self,
        workspace_id: int,
        user_id: int,
        mode: str = 'remote',
        remote_host: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ejecuta Kube-hunter para pentest de Kubernetes."""
        result = self.kubehunter.run_scan(workspace_id, user_id, mode, remote_host)
        
        # Log inicial
        log_to_workspace(
            workspace_id=workspace_id,
            source='KUBEHUNTER',
            level='INFO',
            message=f"Iniciando Kube-hunter: modo {mode}",
            metadata={'scan_id': result.get('scan_id'), 'mode': mode, 'remote_host': remote_host}
        )
        
        return result

    # ============================================
    # KUBE-BENCH (CIS Benchmark)
    # ============================================

    def run_kubebench(
        self,
        workspace_id: int,
        user_id: int,
        targets: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Ejecuta Kube-bench (CIS Kubernetes Benchmark)."""
        result = self.kubebench.run_scan(workspace_id, user_id, targets)
        
        # Log inicial
        log_to_workspace(
            workspace_id=workspace_id,
            source='KUBEBENCH',
            level='INFO',
            message=f"Iniciando Kube-bench: CIS Benchmark",
            metadata={'scan_id': result.get('scan_id'), 'targets': targets}
        )
        
        return result

    # ============================================
    # KUBESCAPE (Kubernetes Security Platform)
    # ============================================

    def run_kubescape(
        self,
        workspace_id: int,
        user_id: int,
        framework: str = 'nsa',
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ejecuta Kubescape para security scanning de K8s."""
        result = self.kubescape.run_scan(workspace_id, user_id, framework, namespace)
        
        # Log inicial
        log_to_workspace(
            workspace_id=workspace_id,
            source='KUBESCAPE',
            level='INFO',
            message=f"Iniciando Kubescape: framework {framework}",
            metadata={'scan_id': result.get('scan_id'), 'framework': framework, 'namespace': namespace}
        )
        
        return result

    # ============================================
    # PREVIEW METHODS
    # ============================================
    
    def preview_trivy_scan(
        self,
        image: str,
        workspace_id: int,
        severity: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Preview del comando Trivy."""
        output_file = f'/workspaces/workspace_{workspace_id}/container_security/trivy_{{scan_id}}.json'
        
        command = [
            'trivy', 'image',
            '--format', 'json',
            '--output', output_file
        ]
        
        if severity:
            command.extend(['--severity', ','.join(severity)])
        
        command.append(image)
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'image': image,
                'severity': severity or ['CRITICAL', 'HIGH']
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_grype_scan(
        self,
        image: str,
        workspace_id: int,
        scope: str = 'all-layers'
    ) -> Dict[str, Any]:
        """Preview del comando Grype."""
        output_file = f'/workspaces/workspace_{workspace_id}/container_security/grype_{{scan_id}}.json'
        
        command = [
            'grype', image,
            '--output', 'json',
            '--file', output_file,
            '--scope', scope
        ]
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'image': image,
                'scope': scope
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_syft_sbom(
        self,
        image: str,
        workspace_id: int,
        output_format: str = 'spdx-json'
    ) -> Dict[str, Any]:
        """Preview del comando Syft."""
        output_file = f'/workspaces/workspace_{workspace_id}/container_security/syft_{{scan_id}}.json'
        
        command = [
            'syft', image,
            '--output', f'{output_format}={output_file}'
        ]
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'image': image,
                'format': output_format
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_kubehunter(
        self,
        workspace_id: int,
        mode: str = 'remote',
        remote_host: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando Kube-hunter."""
        output_file = f'/workspaces/workspace_{workspace_id}/container_security/kubehunter_{{scan_id}}.json'
        
        command = [
            'kube-hunter',
            '--report', 'json',
            '--report-file', output_file
        ]
        
        if mode == 'remote' and remote_host:
            command.extend(['--remote', remote_host])
        elif mode == 'pod':
            command.append('--pod')
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'mode': mode,
                'remote_host': remote_host
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_kubebench(
        self,
        workspace_id: int,
        targets: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Preview del comando Kube-bench."""
        output_file = f'/workspaces/workspace_{workspace_id}/container_security/kubebench_{{scan_id}}.json'
        
        command = [
            'kube-bench',
            '--json',
            '--outputfile', output_file
        ]
        
        if targets:
            command.extend(targets)
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'targets': targets or ['master', 'node', 'etcd', 'policies']
            },
            'estimated_timeout': 300,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    def preview_kubescape(
        self,
        workspace_id: int,
        framework: str = 'nsa',
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Preview del comando Kubescape."""
        output_file = f'/workspaces/workspace_{workspace_id}/container_security/kubescape_{{scan_id}}.json'
        
        command = [
            'kubescape', 'scan',
            'framework', framework,
            '--format', 'json',
            '--output', output_file
        ]
        
        if namespace:
            command.extend(['--namespace', namespace])
        
        command_str = ' '.join(command)
        
        return {
            'command': command,
            'command_string': command_str,
            'parameters': {
                'framework': framework,
                'namespace': namespace
            },
            'estimated_timeout': 600,
            'output_file': output_file,
            'warnings': [],
            'suggestions': []
        }
    
    # ============================================
    # OBTENER RESULTADOS
    # ============================================

    def get_scan_results(self, scan_id: int) -> Dict[str, Any]:
        """Obtiene y parsea resultados de container security scan."""
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
            workspace_output_dir = self._get_workspace_output_dir(scan_id)

            if tool == 'trivy':
                output_file = workspace_output_dir / f'trivy_{scan_id}.json'
                with open(output_file, 'r') as f:
                    results = self.trivy_parser.parse_image_scan(f.read())

            elif tool == 'grype':
                output_file = workspace_output_dir / f'grype_{scan_id}.json'
                with open(output_file, 'r') as f:
                    results = self.grype_parser.parse_results(f.read())

            elif tool == 'syft':
                output_file = workspace_output_dir / f'syft_{scan_id}.json'
                with open(output_file, 'r') as f:
                    results = self.syft_parser.parse_sbom(f.read())

            elif tool == 'kube-hunter':
                output_file = workspace_output_dir / f'kubehunter_{scan_id}.json'
                with open(output_file, 'r') as f:
                    results = self.kubehunter_parser.parse_results(f.read())

            elif tool == 'kube-bench':
                output_file = workspace_output_dir / f'kubebench_{scan_id}.json'
                with open(output_file, 'r') as f:
                    results = self.kubebench_parser.parse_results(f.read())

            elif tool == 'kubescape':
                output_file = workspace_output_dir / f'kubescape_{scan_id}.json'
                with open(output_file, 'r') as f:
                    results = self.kubescape_parser.parse_results(f.read())

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
            logger.error(f"Error parsing container security results {scan_id}: {e}")
            return {
                'scan_id': scan_id,
                'error': f'Failed to parse results: {str(e)}'
            }

