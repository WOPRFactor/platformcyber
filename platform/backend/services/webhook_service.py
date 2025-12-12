"""
Webhook Service
===============

Webhooks para integraciones externas.
"""

import logging
import requests
from typing import Dict, Any, List
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class WebhookService:
    """Servicio de webhooks para integrations."""
    
    def __init__(self):
        """Inicializa webhook service."""
        self.webhooks = {}
        self.delivery_history = []
    
    def register_webhook(
        self,
        webhook_id: str,
        url: str,
        events: List[str],
        secret: str = None,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Registra webhook.
        
        Args:
            webhook_id: ID único del webhook
            url: URL destino
            events: Lista de eventos a escuchar
            secret: Secret para firmar payloads (opcional)
            enabled: Si está habilitado
        
        Returns:
            Dict con webhook registrado
        """
        webhook = {
            'webhook_id': webhook_id,
            'url': url,
            'events': events,
            'secret': secret,
            'enabled': enabled,
            'created_at': datetime.utcnow().isoformat(),
            'deliveries_count': 0,
            'last_delivery': None
        }
        
        self.webhooks[webhook_id] = webhook
        logger.info(f"✅ Webhook registrado: {webhook_id} -> {url}")
        
        return webhook
    
    def trigger_webhook(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Dispara webhooks para evento.
        
        Args:
            event_type: Tipo de evento
            payload: Datos del evento
        
        Returns:
            Lista de resultados de delivery
        """
        results = []
        
        # Encontrar webhooks suscritos a este evento
        matching_webhooks = [
            wh for wh in self.webhooks.values()
            if wh['enabled'] and event_type in wh['events']
        ]
        
        if not matching_webhooks:
            logger.debug(f"No webhooks registered for event: {event_type}")
            return results
        
        logger.info(f"📤 Triggering {len(matching_webhooks)} webhooks for event: {event_type}")
        
        # Enviar a cada webhook
        for webhook in matching_webhooks:
            result = self._deliver_webhook(webhook, event_type, payload)
            results.append(result)
            
            # Actualizar stats
            webhook['deliveries_count'] += 1
            webhook['last_delivery'] = datetime.utcnow().isoformat()
        
        return results
    
    def _deliver_webhook(
        self,
        webhook: Dict[str, Any],
        event_type: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Envía webhook HTTP.
        
        Args:
            webhook: Config del webhook
            event_type: Tipo de evento
            payload: Datos
        
        Returns:
            Resultado de delivery
        """
        webhook_payload = {
            'event': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'webhook_id': webhook['webhook_id'],
            'data': payload
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Cybersecurity-Platform-Webhook/1.0',
            'X-Webhook-Event': event_type
        }
        
        # TODO: Agregar firma HMAC si hay secret
        # if webhook['secret']:
        #     signature = hmac_sign(webhook_payload, webhook['secret'])
        #     headers['X-Webhook-Signature'] = signature
        
        try:
            response = requests.post(
                webhook['url'],
                json=webhook_payload,
                headers=headers,
                timeout=10
            )
            
            delivery_result = {
                'webhook_id': webhook['webhook_id'],
                'event': event_type,
                'status': 'delivered',
                'status_code': response.status_code,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if response.status_code >= 400:
                delivery_result['status'] = 'failed'
                delivery_result['error'] = f"HTTP {response.status_code}"
                logger.error(f"❌ Webhook delivery failed: {webhook['webhook_id']} - HTTP {response.status_code}")
            else:
                logger.info(f"✅ Webhook delivered: {webhook['webhook_id']} - HTTP {response.status_code}")
            
        except Exception as e:
            delivery_result = {
                'webhook_id': webhook['webhook_id'],
                'event': event_type,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
            logger.error(f"❌ Webhook error: {webhook['webhook_id']} - {e}")
        
        # Guardar en historial
        self.delivery_history.append(delivery_result)
        
        return delivery_result
    
    def get_webhooks(self) -> List[Dict[str, Any]]:
        """Obtiene todos los webhooks."""
        return list(self.webhooks.values())
    
    def get_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Obtiene webhook específico."""
        webhook = self.webhooks.get(webhook_id)
        if not webhook:
            raise ValueError(f"Webhook not found: {webhook_id}")
        return webhook
    
    def delete_webhook(self, webhook_id: str) -> bool:
        """Elimina webhook."""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            logger.info(f"🗑️  Webhook eliminado: {webhook_id}")
            return True
        return False
    
    def get_delivery_history(self, webhook_id: str = None) -> List[Dict[str, Any]]:
        """Obtiene historial de deliveries."""
        if webhook_id:
            return [d for d in self.delivery_history if d['webhook_id'] == webhook_id]
        return self.delivery_history


# Singleton
webhook_service = WebhookService()


# ============================================================================
# EVENT TYPES DISPONIBLES
# ============================================================================

EVENT_TYPES = {
    'scan.started': 'Scan iniciado',
    'scan.completed': 'Scan completado',
    'scan.failed': 'Scan falló',
    'vulnerability.found': 'Vulnerabilidad encontrada',
    'vulnerability.critical': 'Vulnerabilidad crítica encontrada',
    'report.generated': 'Reporte generado',
    'user.login': 'Usuario login',
    'workspace.created': 'Workspace creado',
}

