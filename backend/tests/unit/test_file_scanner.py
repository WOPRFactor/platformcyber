"""
Tests Unitarios - FileScanner
==============================

Tests para el escáner de archivos en workspaces.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from services.reporting.core.file_scanner import FileScanner


class TestFileScanner:
    """Tests para FileScanner."""
    
    @pytest.fixture
    def scanner(self):
        """Fixture que retorna instancia de FileScanner."""
        return FileScanner()
    
    @patch('services.reporting.core.file_scanner.get_workspace_dir')
    def test_scan_workspace_finds_files(self, mock_get_dir, scanner, tmp_path):
        """Test que scan_workspace encuentra archivos en categorías."""
        # Crear estructura de workspace simulada
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()
        
        # Crear subdirectorios de categorías
        recon_dir = workspace_dir / "recon"
        recon_dir.mkdir()
        scans_dir = workspace_dir / "scans"
        scans_dir.mkdir()
        
        # Crear archivos de prueba
        (recon_dir / "subfinder_1.txt").write_text("subdomain.example.com")
        (scans_dir / "nmap_1.xml").write_text("<nmaprun></nmaprun>")
        
        mock_get_dir.return_value = workspace_dir
        
        files_by_category = scanner.scan_workspace(1, "Test Workspace")
        
        assert 'recon' in files_by_category
        assert 'scans' in files_by_category
        assert len(files_by_category['recon']) == 1
        assert len(files_by_category['scans']) == 1
    
    @patch('services.reporting.core.file_scanner.get_workspace_dir')
    def test_scan_workspace_empty(self, mock_get_dir, scanner, tmp_path):
        """Test que scan_workspace maneja workspace vacío."""
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()
        
        mock_get_dir.return_value = workspace_dir
        
        files_by_category = scanner.scan_workspace(1, "Test Workspace")
        
        assert files_by_category == {}
    
    @patch('services.reporting.core.file_scanner.get_workspace_dir')
    def test_scan_workspace_nonexistent(self, mock_get_dir, scanner, tmp_path):
        """Test que scan_workspace maneja workspace inexistente."""
        nonexistent_dir = tmp_path / "nonexistent"
        mock_get_dir.return_value = nonexistent_dir
        
        files_by_category = scanner.scan_workspace(1, "Test Workspace")
        
        assert files_by_category == {}
    
    @patch('services.reporting.core.file_scanner.get_workspace_dir')
    def test_scan_workspace_respects_limits(self, mock_get_dir, scanner, tmp_path):
        """Test que scan_workspace respeta límites de archivos."""
        from services.reporting.config import MAX_FILES_PER_CATEGORY
        
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()
        recon_dir = workspace_dir / "recon"
        recon_dir.mkdir()
        
        # Crear más archivos que el límite
        for i in range(MAX_FILES_PER_CATEGORY + 10):
            (recon_dir / f"file_{i}.txt").write_text("content")
        
        mock_get_dir.return_value = workspace_dir
        
        files_by_category = scanner.scan_workspace(1, "Test Workspace")
        
        # Debe limitar a MAX_FILES_PER_CATEGORY
        assert len(files_by_category['recon']) == MAX_FILES_PER_CATEGORY
    
    @patch('services.reporting.core.file_scanner.get_workspace_dir')
    def test_scan_workspace_finds_subdirectories(self, mock_get_dir, scanner, tmp_path):
        """Test que scan_workspace busca en subdirectorios."""
        workspace_dir = tmp_path / "workspace"
        workspace_dir.mkdir()
        scans_dir = workspace_dir / "scans"
        scans_dir.mkdir()
        
        # Crear subdirectorio (simulando sqlmap)
        subdir = scans_dir / "sqlmap_output"
        subdir.mkdir()
        (subdir / "result.json").write_text("{}")
        
        mock_get_dir.return_value = workspace_dir
        
        files_by_category = scanner.scan_workspace(1, "Test Workspace")
        
        # Debe encontrar archivo en subdirectorio
        assert 'scans' in files_by_category
        assert len(files_by_category['scans']) == 1





