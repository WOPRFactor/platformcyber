"""
Configuración del Módulo de Reportería
=======================================

Define límites, configuraciones y constantes para el módulo de reportería.
Todos los límites están diseñados para prevenir DoS y manejar archivos grandes.
"""

# Límites de procesamiento
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB por archivo
MAX_FILES_PER_CATEGORY = 100        # Máximo de archivos por categoría
MAX_TOTAL_FILES = 500               # Máximo de archivos totales a procesar
PROCESSING_TIMEOUT = 300            # 5 minutos timeout para generación

# Parsers
ENABLE_PARALLEL_PARSING = False     # Fase 2: habilitar parsing paralelo
MAX_PARSER_WORKERS = 4              # Para parsing paralelo (Fase 2)

# Reportes
DEFAULT_REPORT_FORMAT = 'pdf'
DEFAULT_REPORT_TYPE = 'technical'
REPORTS_OUTPUT_DIR = 'reports'      # Subdirectorio dentro del workspace

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '[%(asctime)s] %(levelname)s [%(name)s] %(message)s'

# Categorías de archivos soportadas
SUPPORTED_CATEGORIES = [
    'recon',
    'scans',
    'enumeration',
    'vuln_scans',
    'exploitation',
    'postexploit',
    'ad_scans',
    'cloud_scans'
]

# Extensiones de archivos soportadas
SUPPORTED_EXTENSIONS = ['.json', '.xml', '.txt', '.jsonl', '.csv', '.html']
