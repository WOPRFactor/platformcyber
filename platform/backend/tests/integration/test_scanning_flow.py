"""
Test Scanning Flow (Integration)
=================================

Tests de integración para flujo completo de escaneo.
"""

import pytest
from services import ScanningService
from repositories import ScanRepository


class TestScanningFlow:
    """Tests de integración para scanning."""
    
    def test_complete_nmap_flow(self, db, sample_user, sample_workspace):
        """Test flujo completo: crear scan -> ejecutar -> obtener estado."""
        # Arrange
        scan_service = ScanningService()
        
        # Act 1: Crear scan
        result = scan_service.start_nmap_scan(
            target='127.0.0.1',  # localhost
            scan_type='discovery',
            workspace_id=sample_workspace.id,
            user_id=sample_user.id
        )
        
        scan_id = result['scan_id']
        
        # Assert 1: Scan creado
        assert scan_id is not None
        assert result['status'] == 'running'
        
        # Act 2: Obtener estado
        status = scan_service.get_scan_status(scan_id)
        
        # Assert 2: Estado disponible
        assert status['scan_id'] == scan_id
        assert status['target'] == '127.0.0.1'
        assert status['scan_type'] == 'port_scan'
    
    def test_invalid_target_rejected(self, db, sample_user, sample_workspace):
        """Test que targets inválidos son rechazados."""
        scan_service = ScanningService()
        
        with pytest.raises(ValueError):
            scan_service.start_nmap_scan(
                target='256.1.1.1',  # IP inválida
                scan_type='discovery',
                workspace_id=sample_workspace.id,
                user_id=sample_user.id
            )



