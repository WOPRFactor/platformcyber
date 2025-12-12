"""
AI Recommendations Service
===========================

Recomendaciones inteligentes basadas en vulnerabilidades encontradas.
"""

import logging
from typing import List, Dict, Any, Optional
import os

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

logger = logging.getLogger(__name__)


class AIRecommendationsService:
    """Servicio de recomendaciones con IA."""
    
    def __init__(self):
        """Inicializa el servicio de IA."""
        if not GENAI_AVAILABLE:
            self.enabled = False
            self.model = None
            logger.warning("⚠️  AI Recommendations deshabilitado (google.generativeai no disponible)")
            return
            
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.enabled = True
            logger.info("✅ AI Recommendations habilitado (Gemini)")
        else:
            self.enabled = False
            self.model = None
            logger.warning("⚠️  AI Recommendations deshabilitado (no API key)")
    
    def get_exploit_recommendations(
        self,
        vulnerability: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recomienda exploits basados en vulnerabilidad.
        
        Args:
            vulnerability: Dict con datos de vulnerabilidad
        
        Returns:
            Dict con recomendaciones
        """
        if not self.enabled:
            return self._fallback_recommendations(vulnerability)
        
        try:
            prompt = self._build_exploit_prompt(vulnerability)
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'recommendations': response.text,
                'exploits': self._parse_exploit_recommendations(response.text),
                'source': 'ai'
            }
        except Exception as e:
            logger.error(f"❌ Error AI recommendations: {e}")
            return self._fallback_recommendations(vulnerability)
    
    def get_remediation_plan(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Genera plan de remediación priorizado.
        
        Args:
            vulnerabilities: Lista de vulnerabilidades
        
        Returns:
            Dict con plan de remediación
        """
        if not self.enabled:
            return self._fallback_remediation(vulnerabilities)
        
        try:
            prompt = self._build_remediation_prompt(vulnerabilities)
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'plan': response.text,
                'priority': self._parse_priority(vulnerabilities),
                'estimated_time': self._estimate_remediation_time(vulnerabilities),
                'source': 'ai'
            }
        except Exception as e:
            logger.error(f"❌ Error remediation plan: {e}")
            return self._fallback_remediation(vulnerabilities)
    
    def analyze_attack_patterns(
        self,
        scan_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analiza patrones de ataque potenciales.
        
        Args:
            scan_results: Resultados de scans
        
        Returns:
            Dict con análisis de patrones
        """
        if not self.enabled:
            return {'success': False, 'message': 'AI disabled'}
        
        try:
            prompt = self._build_pattern_prompt(scan_results)
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'patterns': response.text,
                'attack_vectors': self._extract_attack_vectors(response.text),
                'source': 'ai'
            }
        except Exception as e:
            logger.error(f"❌ Error pattern analysis: {e}")
            return {'success': False, 'error': str(e)}
    
    def prioritize_targets(
        self,
        targets: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Prioriza targets basándose en contexto.
        
        Args:
            targets: Lista de targets
            context: Contexto adicional (opcional)
        
        Returns:
            Lista de targets priorizados
        """
        if not self.enabled:
            return [{'target': t, 'priority': 'medium', 'reasoning': 'Default'} 
                    for t in targets]
        
        try:
            prompt = self._build_prioritization_prompt(targets, context)
            response = self.model.generate_content(prompt)
            
            return self._parse_prioritized_targets(response.text, targets)
        except Exception as e:
            logger.error(f"❌ Error prioritizing targets: {e}")
            return [{'target': t, 'priority': 'medium', 'reasoning': 'Error'} 
                    for t in targets]
    
    # ========================================================================
    # PROMPT BUILDERS
    # ========================================================================
    
    def _build_exploit_prompt(self, vuln: Dict[str, Any]) -> str:
        """Construye prompt para recomendación de exploits."""
        return f"""
Basándote en la siguiente vulnerabilidad detectada, recomienda exploits apropiados:

**Vulnerabilidad:**
- Tipo: {vuln.get('vulnerability_type', 'Unknown')}
- Severidad: {vuln.get('severity', 'Unknown')}
- Descripción: {vuln.get('description', 'No description')}
- Target: {vuln.get('target', 'Unknown')}
- Puerto: {vuln.get('port', 'Unknown')}

Proporciona:
1. Exploits recomendados (Metasploit modules, scripts)
2. Parámetros sugeridos
3. Precauciones
4. Probabilidad de éxito

Formato: Lista concisa y técnica.
"""
    
    def _build_remediation_prompt(self, vulns: List[Dict]) -> str:
        """Construye prompt para plan de remediación."""
        vuln_summary = "\n".join([
            f"- {v.get('severity', '?').upper()}: {v.get('vulnerability_type', 'Unknown')} "
            f"en {v.get('target', 'Unknown')}"
            for v in vulns[:20]  # Limitar a 20
        ])
        
        return f"""
Genera un plan de remediación priorizado para las siguientes vulnerabilidades:

{vuln_summary}

Incluye:
1. Priorización (CRITICAL primero)
2. Pasos específicos de remediación
3. Tiempo estimado por fix
4. Dependencias entre fixes
5. Quick wins (fixes rápidos de alto impacto)

Formato: Plan estructurado y accionable.
"""
    
    def _build_pattern_prompt(self, results: List[Dict]) -> str:
        """Construye prompt para análisis de patrones."""
        return f"""
Analiza los siguientes resultados de pentesting e identifica patrones de ataque:

Total vulnerabilidades: {len(results)}
Tipos únicos: {len(set(r.get('type') for r in results if r.get('type')))}

Identifica:
1. Vectores de ataque principales
2. Cadenas de explotación posibles
3. Escalación de privilegios probable
4. Movimiento lateral potencial
5. Recomendaciones de pentesting adicional

Formato: Análisis técnico conciso.
"""
    
    def _build_prioritization_prompt(self, targets: List[str], context: Optional[Dict]) -> str:
        """Construye prompt para priorización de targets."""
        context_str = ""
        if context:
            context_str = f"\n\nContexto: {context.get('description', '')}"
        
        targets_list = "\n".join([f"- {t}" for t in targets[:50]])
        
        return f"""
Prioriza los siguientes targets para pentesting:{context_str}

Targets:
{targets_list}

Asigna prioridad (CRITICAL, HIGH, MEDIUM, LOW) basándote en:
1. Probabilidad de vulnerabilidades
2. Impacto potencial
3. Facilidad de explotación
4. Visibilidad (external vs internal)

Formato JSON: [{{"target": "...", "priority": "...", "reasoning": "..."}}]
"""
    
    # ========================================================================
    # PARSERS
    # ========================================================================
    
    def _parse_exploit_recommendations(self, text: str) -> List[Dict[str, Any]]:
        """Parsea recomendaciones de exploits del texto."""
        # Implementación simple - podría mejorarse con parsing más sofisticado
        exploits = []
        lines = text.split('\n')
        
        for line in lines:
            if 'exploit/' in line.lower() or 'msf' in line.lower():
                exploits.append({
                    'exploit': line.strip(),
                    'source': 'ai_recommendation'
                })
        
        return exploits[:5]  # Top 5
    
    def _parse_priority(self, vulns: List[Dict]) -> List[str]:
        """Determina prioridad de remediación."""
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        
        sorted_vulns = sorted(
            vulns,
            key=lambda v: severity_order.get(v.get('severity', 'medium').lower(), 2)
        )
        
        return [v.get('vulnerability_type', 'Unknown') for v in sorted_vulns[:10]]
    
    def _estimate_remediation_time(self, vulns: List[Dict]) -> str:
        """Estima tiempo de remediación."""
        severity_times = {'critical': 4, 'high': 2, 'medium': 1, 'low': 0.5}
        
        total_hours = sum(
            severity_times.get(v.get('severity', 'medium').lower(), 1)
            for v in vulns
        )
        
        if total_hours < 8:
            return f"{total_hours:.1f} hours"
        elif total_hours < 40:
            return f"{total_hours / 8:.1f} days"
        else:
            return f"{total_hours / 40:.1f} weeks"
    
    def _extract_attack_vectors(self, text: str) -> List[str]:
        """Extrae vectores de ataque del análisis."""
        vectors = []
        common_vectors = [
            'SQL Injection', 'XSS', 'CSRF', 'RCE', 'LFI', 'RFI',
            'Authentication Bypass', 'Privilege Escalation', 'SSRF'
        ]
        
        for vector in common_vectors:
            if vector.lower() in text.lower():
                vectors.append(vector)
        
        return vectors
    
    def _parse_prioritized_targets(self, text: str, targets: List[str]) -> List[Dict]:
        """Parsea targets priorizados."""
        # Fallback simple si el parsing JSON falla
        return [
            {
                'target': target,
                'priority': 'medium',
                'reasoning': 'Default prioritization'
            }
            for target in targets
        ]
    
    # ========================================================================
    # FALLBACKS
    # ========================================================================
    
    def _fallback_recommendations(self, vuln: Dict) -> Dict:
        """Recomendaciones fallback sin IA."""
        vuln_type = vuln.get('vulnerability_type', '').lower()
        
        recommendations = {
            'sql': ['sqlmap', 'Manual SQL injection testing'],
            'xss': ['XSS payload testing', 'CSP analysis'],
            'rce': ['Command injection testing', 'Code review'],
        }
        
        for key, rec in recommendations.items():
            if key in vuln_type:
                return {
                    'success': True,
                    'recommendations': '\n'.join(rec),
                    'exploits': [{'exploit': r, 'source': 'fallback'} for r in rec],
                    'source': 'fallback'
                }
        
        return {
            'success': True,
            'recommendations': 'Manual verification recommended',
            'exploits': [],
            'source': 'fallback'
        }
    
    def _fallback_remediation(self, vulns: List[Dict]) -> Dict:
        """Plan de remediación fallback."""
        priority = self._parse_priority(vulns)
        
        return {
            'success': True,
            'plan': f"Remediate vulnerabilities in order of severity:\n" + 
                    "\n".join(f"{i+1}. {p}" for i, p in enumerate(priority)),
            'priority': priority,
            'estimated_time': self._estimate_remediation_time(vulns),
            'source': 'fallback'
        }


# Singleton instance
ai_recommendations_service = AIRecommendationsService()

