"""
Export Service
==============

Exportación de datos en múltiples formatos.
"""

import logging
import json
import csv
from io import StringIO
from typing import List, Dict, Any
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class ExportService:
    """Servicio de exportación de datos."""
    
    def export_vulnerabilities(
        self,
        vulnerabilities: List[Dict[str, Any]],
        format: str = 'json'
    ) -> str:
        """
        Exporta vulnerabilidades.
        
        Args:
            vulnerabilities: Lista de vulnerabilities
            format: Formato (json, csv, xml)
        
        Returns:
            String con datos exportados
        """
        if format.lower() == 'json':
            return self._export_json(vulnerabilities)
        elif format.lower() == 'csv':
            return self._export_csv(vulnerabilities)
        elif format.lower() == 'xml':
            return self._export_xml(vulnerabilities)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def export_scan_results(
        self,
        scan_results: List[Dict[str, Any]],
        format: str = 'json'
    ) -> str:
        """Exporta resultados de scan."""
        return self.export_vulnerabilities(scan_results, format)
    
    def _export_json(self, data: List[Dict]) -> str:
        """Exporta a JSON."""
        return json.dumps(data, indent=2, default=str)
    
    def _export_csv(self, data: List[Dict]) -> str:
        """Exporta a CSV."""
        if not data:
            return ""
        
        output = StringIO()
        
        # Obtener todos los campos únicos
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        
        fieldnames = sorted(list(fieldnames))
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    
    def _export_xml(self, data: List[Dict]) -> str:
        """Exporta a XML."""
        root = ET.Element('data')
        
        for item in data:
            item_element = ET.SubElement(root, 'item')
            for key, value in item.items():
                field = ET.SubElement(item_element, key)
                field.text = str(value)
        
        return ET.tostring(root, encoding='unicode', method='xml')


# Singleton
export_service = ExportService()

