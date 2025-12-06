"""
Test Safe Command Builders
===========================

Tests para constructores de comandos seguros.
"""

import pytest
from utils.commands import SafeNmap, SafeSQLMap, SafeMasscan, SafeHydra


class TestSafeNmap:
    """Tests para SafeNmap."""
    
    def test_build_discovery_scan(self):
        """Test construcción de discovery scan."""
        cmd = SafeNmap.build_discovery_scan('192.168.1.1', 'output')
        
        assert 'nmap' in cmd
        assert '-sS' in cmd
        assert '-p-' in cmd
        assert '--min-rate=1000' in cmd
        assert '192.168.1.1' in cmd
    
    def test_build_detailed_scan(self):
        """Test construcción de detailed scan."""
        cmd = SafeNmap.build_detailed_scan('192.168.1.1', '22,80,443', 'output')
        
        assert '-sV' in cmd
        assert '-sC' in cmd
        assert '22,80,443' in cmd
    
    def test_build_vuln_scan(self):
        """Test construcción de vuln scan (SEGURO)."""
        cmd = SafeNmap.build_vuln_scan('192.168.1.1', output_file='output')
        
        assert '--script' in cmd
        assert 'vuln and safe' in cmd  # Importante: solo scripts seguros
    
    def test_forbidden_script_validation(self):
        """Test validación de scripts prohibidos."""
        with pytest.raises(ValueError):
            SafeNmap.validate_script_args('http-slowloris-check')


class TestSafeSQLMap:
    """Tests para SafeSQLMap."""
    
    def test_build_detection_scan(self):
        """Test construcción de detection scan."""
        cmd = SafeSQLMap.build_detection_scan('http://test.com?id=1')
        
        assert 'sqlmap' in cmd
        assert '--batch' in cmd
        assert '--time-sec' in cmd
        assert '5' in cmd
    
    def test_build_table_dump_with_limit(self):
        """Test dump de tabla CON LÍMITE."""
        cmd = SafeSQLMap.build_table_dump(
            'http://test.com?id=1',
            'dbname',
            'users',
            limit=100
        )
        
        assert '-D' in cmd
        assert 'dbname' in cmd
        assert '-T' in cmd
        assert 'users' in cmd
        assert '--stop' in cmd
        assert '100' in cmd
    
    def test_limit_enforcement(self):
        """Test que el límite se aplica."""
        cmd = SafeSQLMap.build_table_dump(
            'http://test.com?id=1',
            'db',
            'table',
            limit=10000  # Muy alto
        )
        
        # Debe limitarse a 1000
        stop_index = cmd.index('--stop')
        assert cmd[stop_index + 1] == '1000'
    
    def test_forbidden_options_validation(self):
        """Test validación de opciones prohibidas."""
        with pytest.raises(ValueError):
            SafeSQLMap.validate_options(['--dump-all'])
        
        with pytest.raises(ValueError):
            SafeSQLMap.validate_options(['--os-shell'])
    
    def test_risk_level_validation(self):
        """Test validación de nivel de risk."""
        with pytest.raises(ValueError):
            SafeSQLMap.build_advanced_scan(
                'http://test.com?id=1',
                risk=3  # Muy alto
            )


class TestSafeMasscan:
    """Tests para SafeMasscan."""
    
    def test_build_scan_internal(self):
        """Test construcción de scan interno."""
        cmd = SafeMasscan.build_scan(
            '192.168.1.0/24',
            '1-65535',
            'internal',
            'output.json'
        )
        
        assert 'masscan' in cmd
        assert '--rate' in cmd
        assert '1000' in cmd  # Rate para internal
        assert '--max-rate' in cmd  # Hard limit
    
    def test_build_scan_stealth(self):
        """Test construcción de scan sigiloso."""
        cmd = SafeMasscan.build_scan(
            '192.168.1.1',
            '1-1000',
            'stealth',
            'output.json'
        )
        
        assert '--rate' in cmd
        assert '100' in cmd  # Rate bajo para stealth
    
    def test_rate_limit_enforcement(self):
        """Test que el rate limit se aplica."""
        with pytest.raises(ValueError):
            SafeMasscan.build_custom_rate_scan(
                '192.168.1.1',
                '1-65535',
                rate=10000  # Muy alto
            )


class TestSafeHydra:
    """Tests para SafeHydra."""
    
    def test_build_ssh_attack(self):
        """Test construcción de ataque SSH."""
        cmd = SafeHydra.build_ssh_attack(
            '192.168.1.1',
            username='admin',
            passfile='passwords.txt'
        )
        
        assert 'hydra' in cmd
        assert '-l' in cmd
        assert 'admin' in cmd
        assert '-P' in cmd
        assert '-t' in cmd
        assert '4' in cmd  # Max 4 threads
        assert '-f' in cmd  # Stop on success
    
    def test_max_threads_limit(self):
        """Test que el límite de threads se aplica."""
        cmd = SafeHydra.build_ssh_attack(
            '192.168.1.1',
            username='admin',
            password='test'
        )
        
        # Buscar -t (threads)
        t_index = cmd.index('-t')
        threads = int(cmd[t_index + 1])
        
        assert threads <= SafeHydra.MAX_THREADS
    
    def test_service_validation(self):
        """Test validación de servicios."""
        assert SafeHydra.validate_service('ssh')
        
        with pytest.raises(ValueError):
            SafeHydra.validate_service('invalid_service')



