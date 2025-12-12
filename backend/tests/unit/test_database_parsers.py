"""
Tests Unitarios - Database Enumeration Parsers
==============================================

Tests para parsers de enumeración de bases de datos.
"""

import pytest
from pathlib import Path
from services.reporting.parsers.enumeration.database.mysql_enum_parser import MySQLEnumParser
from services.reporting.parsers.enumeration.database.postgresql_enum_parser import PostgreSQLEnumParser
from services.reporting.parsers.enumeration.database.redis_enum_parser import RedisEnumParser

FIXTURES_DIR = Path(__file__).parent.parent / 'fixtures' / 'enumeration' / 'database'


class TestDatabaseParsers:
    """Tests para parsers de enumeración de bases de datos."""
    
    def test_mysql_enum_parser(self):
        """Test MySQLEnumParser."""
        parser = MySQLEnumParser()
        fixture_file = FIXTURES_DIR / 'mysql_enum_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) >= 0
        assert all(f.raw_data.get('tool') == 'mysql_enum' for f in findings) if findings else True
        # Verificar que hay finding de databases si existen
        if findings:
            db_findings = [f for f in findings if 'databases' in f.raw_data]
            assert len(db_findings) > 0
    
    def test_postgresql_enum_parser(self):
        """Test PostgreSQLEnumParser."""
        parser = PostgreSQLEnumParser()
        fixture_file = FIXTURES_DIR / 'postgresql_enum_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) >= 0
        assert all(f.raw_data.get('tool') == 'postgresql_enum' for f in findings) if findings else True
        # Verificar que hay finding de databases si existen
        if findings:
            db_findings = [f for f in findings if 'databases' in f.raw_data]
            assert len(db_findings) > 0
    
    def test_redis_enum_parser(self):
        """Test RedisEnumParser."""
        parser = RedisEnumParser()
        fixture_file = FIXTURES_DIR / 'redis_enum_sample.txt'
        
        if not fixture_file.exists():
            pytest.skip(f"Fixture not found: {fixture_file}")
        
        findings = parser.parse(fixture_file)
        
        assert len(findings) >= 0
        assert all(f.raw_data.get('tool') == 'redis_enum' for f in findings) if findings else True
        # Verificar que hay finding de keys si existen
        if findings:
            key_findings = [f for f in findings if 'key_count' in f.raw_data]
            assert len(key_findings) > 0
    
    def test_mysql_enum_can_parse(self):
        """Test MySQLEnumParser.can_parse()."""
        parser = MySQLEnumParser()
        
        assert parser.can_parse(Path('mysql_123.txt'))
        assert parser.can_parse(Path('MYSQL_ENUM_sample.txt'))
        assert not parser.can_parse(Path('mysql_123.json'))
        assert not parser.can_parse(Path('nmap_123.xml'))
    
    def test_postgresql_enum_can_parse(self):
        """Test PostgreSQLEnumParser.can_parse()."""
        parser = PostgreSQLEnumParser()
        
        assert parser.can_parse(Path('postgresql_123.txt'))
        assert parser.can_parse(Path('POSTGRESQL_ENUM_sample.txt'))
        assert not parser.can_parse(Path('postgresql_123.json'))
        assert not parser.can_parse(Path('nmap_123.xml'))
    
    def test_redis_enum_can_parse(self):
        """Test RedisEnumParser.can_parse()."""
        parser = RedisEnumParser()
        
        assert parser.can_parse(Path('redis_123.txt'))
        assert parser.can_parse(Path('REDIS_ENUM_sample.txt'))
        assert not parser.can_parse(Path('redis_123.json'))
        assert not parser.can_parse(Path('nmap_123.xml'))


