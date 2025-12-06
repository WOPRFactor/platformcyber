"""
MITRE ATT&CK Service
====================

Servicio principal para simulación y tracking de técnicas MITRE ATT&CK.
"""

import logging
from typing import Dict, List, Any, Optional

from .tactics import get_tactics
from .techniques import get_techniques
from .kill_chains import get_kill_chains
from .campaigns import CampaignsManager

logger = logging.getLogger(__name__)


class MitreAttackService:
    """Servicio para MITRE ATT&CK Framework."""
    
    def __init__(self):
        """Inicializa el servicio MITRE ATT&CK."""
        self.tactics = get_tactics()
        self.techniques = get_techniques()
        self.kill_chains = get_kill_chains()
        self.campaigns_manager = CampaignsManager()
        logger.info("✅ MITRE ATT&CK Service inicializado")
    
    def get_all_tactics(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene todas las tácticas."""
        logger.info("Obteniendo todas las tácticas MITRE")
        return self.tactics
    
    def get_tactic(self, tactic_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una táctica específica."""
        logger.info(f"Obteniendo táctica: {tactic_id}")
        return self.tactics.get(tactic_id)
    
    def get_all_techniques(
        self,
        tactic_filter: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Obtiene todas las técnicas, opcionalmente filtradas por táctica."""
        techniques = self.techniques
        
        if tactic_filter:
            techniques = {
                tid: tech for tid, tech in techniques.items()
                if tech['tactic'] == tactic_filter
            }
            logger.info(f"Técnicas filtradas por {tactic_filter}: {len(techniques)}")
        else:
            logger.info(f"Obteniendo todas las técnicas: {len(techniques)}")
        
        return techniques
    
    def get_technique(self, technique_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una técnica específica."""
        logger.info(f"Obteniendo técnica: {technique_id}")
        return self.techniques.get(technique_id)
    
    def create_campaign(
        self,
        name: str,
        workspace_id: int,
        techniques: List[str],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Crea una campaña de simulación."""
        return self.campaigns_manager.create_campaign(name, workspace_id, techniques, description)
    
    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene detalles de una campaña."""
        return self.campaigns_manager.get_campaign(campaign_id)
    
    def list_campaigns(self, workspace_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Lista todas las campañas."""
        return self.campaigns_manager.list_campaigns(workspace_id)
    
    def preview_technique(
        self,
        technique_id: str,
        target: Optional[str] = None,
        workspace_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Preview de una técnica MITRE ATT&CK (sin ejecutar).
        
        Args:
            technique_id: ID de la técnica (ej: T1566)
            target: Target opcional
            workspace_id: ID del workspace
            
        Returns:
            Dict con preview del comando y parámetros
        """
        technique = self.techniques.get(technique_id)
        if not technique:
            return {
                'error': 'Technique not found',
                'command': [],
                'command_string': ''
            }
        
        # Construir comando simulado basado en la técnica
        command_parts = ['mitre-attack', '--technique', technique_id]
        
        if target:
            command_parts.extend(['--target', target])
        
        # Agregar opciones basadas en la técnica
        if technique.get('platforms'):
            command_parts.extend(['--platforms', ','.join(technique['platforms'])])
        
        command_str = ' '.join(command_parts)
        
        # Calcular tiempo estimado basado en severidad
        severity_timeout = {
            'critical': 3600,
            'high': 1800,
            'medium': 900,
            'low': 300
        }
        estimated_timeout = severity_timeout.get(technique.get('severity', 'medium'), 900)
        
        return {
            'command': command_parts,
            'command_string': command_str,
            'parameters': {
                'technique_id': technique_id,
                'technique_name': technique.get('name', ''),
                'tactic': technique.get('tactic', ''),
                'target': target,
                'workspace_id': workspace_id
            },
            'estimated_timeout': estimated_timeout,
            'technique_info': {
                'id': technique_id,
                'name': technique.get('name', ''),
                'description': technique.get('description', ''),
                'tactic': technique.get('tactic', ''),
                'severity': technique.get('severity', 'medium'),
                'platforms': technique.get('platforms', [])
            },
            'output_file': f'/workspaces/workspace_{workspace_id or "X"}/mitre_attacks/{technique_id}_{{timestamp}}.json',
            'warnings': [
                'Las técnicas MITRE ATT&CK pueden ser peligrosas en entornos de producción',
                'Asegúrate de tener permisos y autorización para ejecutar esta técnica',
                'Algunas técnicas pueden generar alertas de seguridad',
                'Ejecuta solo en entornos controlados y autorizados'
            ],
            'suggestions': [
                'Revisa la documentación de la técnica antes de ejecutar',
                'Verifica que el target esté en un entorno de pruebas',
                'Considera ejecutar en modo dry-run primero',
                'Monitorea los logs después de la ejecución'
            ]
        }

    def execute_technique(
        self,
        campaign_id: str,
        technique_id: str,
        target: Optional[str] = None
    ) -> Dict[str, Any]:
        """Simula ejecución de una técnica (modo seguro)."""
        technique = self.techniques.get(technique_id)
        if not technique:
            return {'success': False, 'error': 'Technique not found'}
        
        # Logging al workspace
        campaign = self.campaigns_manager.get_campaign(campaign_id)
        if campaign:
            workspace_id = campaign.get('workspace_id')
            if workspace_id:
                from utils.workspace_logger import log_to_workspace
                log_to_workspace(
                    workspace_id=workspace_id,
                    source='MITRE',
                    level='INFO',
                    message=f"Ejecutando técnica MITRE: {technique_id}",
                    metadata={
                        'campaign_id': campaign_id,
                        'technique_id': technique_id,
                        'technique_name': technique.get('name', ''),
                        'target': target
                    }
                )
        
        return self.campaigns_manager.execute_technique(campaign_id, technique_id, technique, target)
    
    def get_coverage_matrix(self) -> Dict[str, Any]:
        """
        Calcula matriz de cobertura de detección.
        
        Returns:
            Dict con estadísticas de cobertura
        """
        total_techniques = len(self.techniques)
        
        # Simular cobertura (en producción esto vendría de configuración real)
        covered_techniques = int(total_techniques * 0.65)  # 65% cobertura ejemplo
        
        coverage_by_tactic = {}
        for tactic_id, tactic in self.tactics.items():
            tactic_techniques = [
                t for t in self.techniques.values()
                if t['tactic'] == tactic_id
            ]
            covered = int(len(tactic_techniques) * 0.65)
            coverage_by_tactic[tactic_id] = {
                'name': tactic['name'],
                'total': len(tactic_techniques),
                'covered': covered,
                'coverage_percent': round((covered / len(tactic_techniques) * 100) if tactic_techniques else 0, 1)
            }
        
        logger.info("📊 Calculando matriz de cobertura")
        
        return {
            'total_techniques': total_techniques,
            'covered_techniques': covered_techniques,
            'coverage_percent': round((covered_techniques / total_techniques * 100), 1),
            'by_tactic': coverage_by_tactic,
            'gaps': [
                {
                    'technique_id': 'T1068',
                    'name': 'Exploitation for Privilege Escalation',
                    'severity': 'high'
                },
                {
                    'technique_id': 'T1055',
                    'name': 'Process Injection',
                    'severity': 'high'
                }
            ]
        }
    
    def get_kill_chains(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene kill chains predefinidos."""
        logger.info("⚔️  Obteniendo kill chains")
        return self.kill_chains
    
    def get_kill_chain(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un kill chain específico."""
        logger.info(f"⚔️  Obteniendo kill chain: {chain_id}")
        return self.kill_chains.get(chain_id)


# Singleton
mitre_service = MitreAttackService()


