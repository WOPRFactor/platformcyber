"""
Notification Service
====================

Notificaciones por email, Slack, Discord.
"""

import logging
import requests
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio de notificaciones multi-canal."""
    
    def __init__(self):
        """Inicializa notification service."""
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        logger.info("✅ Notification Service inicializado")
    
    def notify_vulnerability_found(
        self,
        severity: str,
        vulnerability_type: str,
        target: str,
        channels: list = ['slack', 'discord']
    ) -> Dict[str, Any]:
        """
        Notifica vulnerabilidad encontrada.
        
        Args:
            severity: Severidad
            vulnerability_type: Tipo
            target: Target
            channels: Canales (slack, discord, email)
        
        Returns:
            Resultados de envío
        """
        message = self._format_vulnerability_message(severity, vulnerability_type, target)
        
        results = {}
        
        if 'slack' in channels and self.slack_webhook:
            results['slack'] = self._send_slack(message, severity)
        
        if 'discord' in channels and self.discord_webhook:
            results['discord'] = self._send_discord(message, severity)
        
        return results
    
    def notify_scan_completed(
        self,
        scan_type: str,
        target: str,
        vulnerabilities_count: int,
        channels: list = ['slack']
    ) -> Dict[str, Any]:
        """Notifica scan completado."""
        message = f"🎯 **Scan Completado**\n\n" \
                  f"Tipo: {scan_type}\n" \
                  f"Target: {target}\n" \
                  f"Vulnerabilidades: {vulnerabilities_count}"
        
        results = {}
        
        if 'slack' in channels and self.slack_webhook:
            results['slack'] = self._send_slack(message)
        
        if 'discord' in channels and self.discord_webhook:
            results['discord'] = self._send_discord(message)
        
        return results
    
    def _format_vulnerability_message(
        self,
        severity: str,
        vuln_type: str,
        target: str
    ) -> str:
        """Formatea mensaje de vulnerabilidad."""
        emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢',
            'info': '🔵'
        }.get(severity.lower(), '⚪')
        
        return f"{emoji} **{severity.upper()} Vulnerability Found**\n\n" \
               f"Type: {vuln_type}\n" \
               f"Target: {target}\n" \
               f"Action: Immediate review recommended"
    
    def _send_slack(self, message: str, severity: str = 'info') -> Dict[str, Any]:
        """Envía notificación a Slack."""
        if not self.slack_webhook:
            return {'success': False, 'error': 'Slack webhook not configured'}
        
        try:
            # Color por severidad
            colors = {
                'critical': 'danger',
                'high': 'warning',
                'medium': '#ffcc00',
                'low': 'good',
                'info': '#0066cc'
            }
            
            payload = {
                'text': 'Cybersecurity Platform Alert',
                'attachments': [{
                    'text': message,
                    'color': colors.get(severity.lower(), '#0066cc'),
                    'footer': 'Cybersecurity Platform',
                    'ts': int(time.time())
                }]
            }
            
            response = requests.post(self.slack_webhook, json=payload, timeout=5)
            
            if response.status_code == 200:
                logger.info("✅ Slack notification sent")
                return {'success': True, 'channel': 'slack'}
            else:
                logger.error(f"❌ Slack error: HTTP {response.status_code}")
                return {'success': False, 'error': f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Slack error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _send_discord(self, message: str, severity: str = 'info') -> Dict[str, Any]:
        """Envía notificación a Discord."""
        if not self.discord_webhook:
            return {'success': False, 'error': 'Discord webhook not configured'}
        
        try:
            # Color por severidad (decimal)
            colors = {
                'critical': 16711680,  # Rojo
                'high': 16753920,      # Naranja
                'medium': 16776960,    # Amarillo
                'low': 65280,          # Verde
                'info': 255            # Azul
            }
            
            payload = {
                'embeds': [{
                    'title': 'Cybersecurity Platform Alert',
                    'description': message,
                    'color': colors.get(severity.lower(), 255),
                    'footer': {'text': 'Cybersecurity Platform'}
                }]
            }
            
            response = requests.post(self.discord_webhook, json=payload, timeout=5)
            
            if response.status_code == 204:
                logger.info("✅ Discord notification sent")
                return {'success': True, 'channel': 'discord'}
            else:
                logger.error(f"❌ Discord error: HTTP {response.status_code}")
                return {'success': False, 'error': f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Discord error: {e}")
            return {'success': False, 'error': str(e)}


# Fix import
import time

# Singleton
notification_service = NotificationService()

