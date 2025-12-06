"""
Safe SQLMap Command Builder
============================

Constructor seguro de comandos SQLMap para prevenir daños.
"""

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class SafeSQLMap:
    """
    Constructor seguro de comandos SQLMap.
    
    PREVIENE:
    - --dump-all (puede dumpear TODA la BD)
    - --os-shell (ejecución de comandos)
    - --os-cmd (ejecución de comandos)
    - Risk > 2 o Level > 3 (demasiado agresivo)
    - Threads > 5 (puede causar DoS)
    """
    
    # Opciones PROHIBIDAS
    FORBIDDEN_OPTIONS = [
        '--dump-all',
        '--os-shell',
        '--os-cmd',
        '--sql-shell',
        '--file-write',
        '--file-dest'
    ]
    
    # Límites de seguridad
    MAX_RISK = 2
    MAX_LEVEL = 3
    MAX_THREADS = 5
    
    @classmethod
    def build_detection_scan(cls, url: str, cookies: Optional[str] = None) -> List[str]:
        """
        Escaneo de detección de SQLi (solo identifica vulnerabilidad).
        
        Args:
            url: URL objetivo
            cookies: Cookies de sesión (opcional)
        
        Returns:
            Comando listo para ejecutar
        """
        cmd = [
            'sqlmap',
            '-u', url,
            '--batch',          # Sin confirmaciones
            '--random-agent',   # User-agent aleatorio
            '--time-sec', '5',  # Timeout por query
            '--retries', '2',   # Máximo 2 reintentos
            '--threads', '1',   # Single thread para detección
        ]
        
        if cookies:
            cmd.extend(['--cookie', cookies])
        
        logger.info(f"SQLMap detection en {url}")
        return cmd
    
    @classmethod
    def build_enumeration_scan(
        cls,
        url: str,
        database: Optional[str] = None,
        cookies: Optional[str] = None
    ) -> List[str]:
        """
        Enumeración de bases de datos y tablas (NO dumpea datos).
        
        Args:
            url: URL objetivo
            database: Base de datos específica (opcional)
            cookies: Cookies de sesión (opcional)
        
        Returns:
            Comando listo para ejecutar
        """
        cmd = [
            'sqlmap',
            '-u', url,
            '--batch',
            '--random-agent',
            '--time-sec', '5',
            '--retries', '2',
            '--threads', '2',
        ]
        
        if cookies:
            cmd.extend(['--cookie', cookies])
        
        if database:
            cmd.extend(['-D', database, '--tables'])  # Solo listar tablas
        else:
            cmd.append('--dbs')  # Solo listar bases de datos
        
        logger.info(f"SQLMap enumeration en {url}")
        return cmd
    
    @classmethod
    def build_table_dump(
        cls,
        url: str,
        database: str,
        table: str,
        columns: Optional[str] = None,
        limit: int = 100,
        cookies: Optional[str] = None
    ) -> List[str]:
        """
        Dump de una tabla ESPECÍFICA con LÍMITE de filas.
        
        Args:
            url: URL objetivo
            database: Nombre de la base de datos
            table: Nombre de la tabla
            columns: Columnas específicas (opcional, ej: 'username,password')
            limit: Límite de filas a dumpear (default: 100)
            cookies: Cookies de sesión (opcional)
        
        Returns:
            Comando listo para ejecutar
        
        Note:
            NUNCA usa --dump-all, siempre especifica tabla y límite
        """
        if limit > 1000:
            logger.warning(f"Límite de {limit} filas es alto, reduciendo a 1000")
            limit = 1000
        
        cmd = [
            'sqlmap',
            '-u', url,
            '-D', database,
            '-T', table,
            '--batch',
            '--random-agent',
            '--time-sec', '5',
            '--retries', '2',
            '--threads', '3',
            '--start', '1',
            '--stop', str(limit),  # Limitar filas
            '--dump',
        ]
        
        if columns:
            cmd.extend(['-C', columns])
        
        if cookies:
            cmd.extend(['--cookie', cookies])
        
        logger.info(f"SQLMap dump de {database}.{table} (límite: {limit} filas)")
        return cmd
    
    @classmethod
    def build_advanced_scan(
        cls,
        url: str,
        risk: int = 1,
        level: int = 1,
        tamper: Optional[str] = None,
        cookies: Optional[str] = None
    ) -> List[str]:
        """
        Escaneo avanzado con opciones de evasión.
        
        Args:
            url: URL objetivo
            risk: Nivel de risk (1-2, máximo 2)
            level: Nivel de checks (1-3, máximo 3)
            tamper: Scripts de tamper para WAF bypass (ej: 'space2comment')
            cookies: Cookies de sesión (opcional)
        
        Returns:
            Comando listo para ejecutar
        
        Raises:
            ValueError: Si risk > 2 o level > 3
        """
        if risk > cls.MAX_RISK:
            raise ValueError(f"Risk máximo permitido: {cls.MAX_RISK}, solicitado: {risk}")
        
        if level > cls.MAX_LEVEL:
            raise ValueError(f"Level máximo permitido: {cls.MAX_LEVEL}, solicitado: {level}")
        
        cmd = [
            'sqlmap',
            '-u', url,
            '--batch',
            '--random-agent',
            '--level', str(level),
            '--risk', str(risk),
            '--time-sec', '5',
            '--retries', '2',
            '--threads', '3',
        ]
        
        if tamper:
            cmd.extend(['--tamper', tamper])
        
        if cookies:
            cmd.extend(['--cookie', cookies])
        
        logger.info(f"SQLMap advanced scan en {url} (risk:{risk}, level:{level})")
        return cmd
    
    @classmethod
    def build_injection_test(
        cls,
        url: str,
        output_dir: str,
        method: str = 'GET',
        data: Optional[str] = None,
        cookie: Optional[str] = None,
        risk: int = 1,
        level: int = 1
    ) -> List[str]:
        """
        Escaneo de inyección SQL con opciones configurables.
        
        Args:
            url: URL objetivo
            output_dir: Directorio de salida
            method: Método HTTP ('GET' o 'POST')
            data: Datos POST (opcional)
            cookie: Cookies de sesión (opcional)
            risk: Nivel de risk (1-2, máximo 2)
            level: Nivel de checks (1-3, máximo 3)
        
        Returns:
            Comando listo para ejecutar
        
        Raises:
            ValueError: Si risk > 2 o level > 3
        """
        if risk > cls.MAX_RISK:
            raise ValueError(f"Risk máximo permitido: {cls.MAX_RISK}, solicitado: {risk}")
        
        if level > cls.MAX_LEVEL:
            raise ValueError(f"Level máximo permitido: {cls.MAX_LEVEL}, solicitado: {level}")
        
        cmd = [
            'sqlmap',
            '-u', url,
            '--batch',
            '--random-agent',
            '--level', str(level),
            '--risk', str(risk),
            '--time-sec', '5',
            '--retries', '2',
            '--threads', '3',
            '--output-dir', output_dir
        ]
        
        if method.upper() == 'POST' and data:
            cmd.extend(['--data', data])
        
        if cookie:
            cmd.extend(['--cookie', cookie])
        
        logger.info(f"SQLMap injection test en {url} (method:{method}, risk:{risk}, level:{level})")
        return cmd
    
    @classmethod
    def validate_options(cls, options: List[str]) -> bool:
        """
        Valida que las opciones no contengan comandos prohibidos.
        
        Args:
            options: Lista de opciones de SQLMap
        
        Returns:
            True si son seguras
        
        Raises:
            ValueError: Si contiene opciones prohibidas
        """
        for option in options:
            if option in cls.FORBIDDEN_OPTIONS:
                raise ValueError(
                    f"Opción prohibida: {option}\n"
                    f"Esta opción puede causar daño severo al servidor objetivo."
                )
        
        return True



