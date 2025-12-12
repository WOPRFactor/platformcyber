"""
Response Compression
====================

Middleware para comprimir respuestas HTTP (gzip).
"""

import gzip
from io import BytesIO
from flask import Flask, request
import logging

logger = logging.getLogger(__name__)


def setup_compression(app: Flask, min_size: int = 500) -> None:
    """
    Configura compresión gzip para respuestas.
    
    Args:
        app: Instancia Flask
        min_size: Tamaño mínimo en bytes para comprimir (default: 500)
    """
    
    @app.after_request
    def compress_response(response):
        """
        Comprime respuesta si el cliente acepta gzip.
        """
        # Solo comprimir si:
        # 1. Cliente acepta gzip
        # 2. Respuesta > min_size
        # 3. Content-Type es comprimible
        # 4. No está ya comprimida
        
        accept_encoding = request.headers.get('Accept-Encoding', '')
        
        if 'gzip' not in accept_encoding.lower():
            return response
        
        if response.status_code < 200 or response.status_code >= 300:
            return response
        
        if 'Content-Encoding' in response.headers:
            return response
        
        if response.direct_passthrough:
            return response
        
        # Tipos comprimibles
        compressible_types = [
            'text/',
            'application/json',
            'application/javascript',
            'application/xml',
            'application/xhtml+xml'
        ]
        
        content_type = response.headers.get('Content-Type', '')
        if not any(t in content_type for t in compressible_types):
            return response
        
        # Obtener data
        data = response.get_data()
        
        if len(data) < min_size:
            return response
        
        # Comprimir
        try:
            gzip_buffer = BytesIO()
            with gzip.GzipFile(mode='wb', fileobj=gzip_buffer, compresslevel=6) as gzip_file:
                gzip_file.write(data)
            
            compressed_data = gzip_buffer.getvalue()
            
            # Solo usar comprimido si es más pequeño
            if len(compressed_data) < len(data):
                response.set_data(compressed_data)
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Content-Length'] = len(compressed_data)
                response.headers['Vary'] = 'Accept-Encoding'
                
                compression_ratio = (1 - len(compressed_data) / len(data)) * 100
                logger.debug(f"📦 Compressed response: {len(data)}B → {len(compressed_data)}B ({compression_ratio:.1f}% reduction)")
            
        except Exception as e:
            logger.error(f"❌ Compression error: {e}")
            # En caso de error, devolver respuesta sin comprimir
        
        return response
    
    logger.info("✅ Response compression configurado (gzip)")

