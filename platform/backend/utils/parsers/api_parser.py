"""
API Testing Parsers
===================

Parsers para herramientas de API pentesting.
"""

import json
import re
from typing import Dict, List, Any, Optional


class ArjunParser:
    """Parser para resultados de Arjun (parameter discovery)."""
    
    @staticmethod
    def parse_output(output: str) -> Dict[str, Any]:
        """
        Parsea la salida de Arjun.
        
        Arjun imprime parámetros encontrados en formato:
        [+] Discovered parameters: param1, param2, param3
        """
        parameters = {
            'get_params': [],
            'post_params': [],
            'json_params': [],
            'total': 0
        }
        
        # Buscar líneas con parámetros descubiertos
        for line in output.split('\n'):
            if 'parameters' in line.lower() and '[+]' in line:
                # Extraer parámetros de la línea
                match = re.search(r'parameters?:\s*(.+)', line, re.IGNORECASE)
                if match:
                    params_str = match.group(1).strip()
                    # Separar por comas
                    params = [p.strip() for p in params_str.split(',') if p.strip()]
                    
                    # Determinar tipo de parámetro
                    if 'GET' in line:
                        parameters['get_params'].extend(params)
                    elif 'POST' in line:
                        parameters['post_params'].extend(params)
                    elif 'JSON' in line:
                        parameters['json_params'].extend(params)
                    else:
                        # Si no se especifica, asumir GET
                        parameters['get_params'].extend(params)
        
        # Eliminar duplicados
        parameters['get_params'] = list(set(parameters['get_params']))
        parameters['post_params'] = list(set(parameters['post_params']))
        parameters['json_params'] = list(set(parameters['json_params']))
        parameters['total'] = (
            len(parameters['get_params']) + 
            len(parameters['post_params']) + 
            len(parameters['json_params'])
        )
        
        return {
            'tool': 'arjun',
            'parameters': parameters
        }


class KiterunnerParser:
    """Parser para resultados de Kiterunner (API route discovery)."""
    
    @staticmethod
    def parse_output(output: str) -> Dict[str, Any]:
        """
        Parsea la salida de Kiterunner.
        
        Formato típico:
        GET     200 [    123,   4,   1] https://example.com/api/v1/users
        POST    403 [     45,   2,   1] https://example.com/api/v1/admin
        """
        routes = []
        
        for line in output.split('\n'):
            # Buscar líneas con métodos HTTP
            match = re.match(
                r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+(\d{3})\s+\[([^\]]+)\]\s+(\S+)',
                line.strip()
            )
            
            if match:
                method = match.group(1)
                status_code = int(match.group(2))
                stats = match.group(3).strip()  # Size, words, lines
                url = match.group(4)
                
                routes.append({
                    'method': method,
                    'status_code': status_code,
                    'url': url,
                    'stats': stats
                })
        
        # Agrupar por status code
        by_status = {}
        for route in routes:
            status = route['status_code']
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(route)
        
        return {
            'tool': 'kiterunner',
            'total_routes': len(routes),
            'routes': routes,
            'by_status': {str(k): len(v) for k, v in by_status.items()},
            'interesting': [r for r in routes if r['status_code'] in [200, 201, 301, 302, 401, 403]]
        }


class JWTToolParser:
    """Parser para resultados de JWT_Tool."""
    
    @staticmethod
    def parse_jwt_info(output: str) -> Dict[str, Any]:
        """
        Parsea la información de un JWT token.
        """
        jwt_info = {
            'header': {},
            'payload': {},
            'signature': '',
            'vulnerabilities': [],
            'algorithm': 'unknown'
        }
        
        # Intentar extraer JSON del output
        # JWT_Tool suele imprimir el header y payload en formato JSON
        json_blocks = re.findall(r'\{[^\{\}]+\}', output)
        
        for i, block in enumerate(json_blocks):
            try:
                data = json.loads(block)
                if i == 0:  # Primer bloque = header
                    jwt_info['header'] = data
                    jwt_info['algorithm'] = data.get('alg', 'unknown')
                elif i == 1:  # Segundo bloque = payload
                    jwt_info['payload'] = data
            except json.JSONDecodeError:
                continue
        
        # Buscar vulnerabilidades reportadas
        vuln_keywords = [
            'none algorithm', 'weak secret', 'algorithm confusion',
            'signature not verified', 'expired', 'invalid signature'
        ]
        
        for keyword in vuln_keywords:
            if keyword.lower() in output.lower():
                jwt_info['vulnerabilities'].append(keyword)
        
        return {
            'tool': 'jwt_tool',
            'jwt_info': jwt_info
        }


class FFUFParser:
    """Parser para resultados de FFUF (fuzzer)."""
    
    @staticmethod
    def parse_json(json_str: str) -> Dict[str, Any]:
        """
        Parsea la salida JSON de FFUF.
        
        FFUF con -o output.json genera JSON estructurado.
        """
        try:
            data = json.loads(json_str)
            
            results = data.get('results', [])
            
            # Filtrar por status code interesante
            interesting = [
                r for r in results 
                if r.get('status') in [200, 201, 204, 301, 302, 401, 403, 500]
            ]
            
            # Agrupar por status
            by_status = {}
            for result in results:
                status = result.get('status')
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append(result)
            
            return {
                'tool': 'ffuf',
                'total_results': len(results),
                'interesting_results': len(interesting),
                'results': interesting[:100],  # Primeros 100
                'by_status': {str(k): len(v) for k, v in by_status.items()},
                'config': data.get('config', {})
            }
            
        except json.JSONDecodeError:
            return {
                'tool': 'ffuf',
                'error': 'Failed to parse FFUF JSON output'
            }
    
    @staticmethod
    def parse_text(output: str) -> Dict[str, Any]:
        """
        Parsea la salida de texto de FFUF.
        """
        results = []
        
        for line in output.split('\n'):
            # Buscar líneas con resultados
            # Formato típico: [Status: 200, Size: 1234, Words: 56, Lines: 12]
            match = re.search(
                r'\[Status:\s*(\d+).*?Size:\s*(\d+).*?Words:\s*(\d+).*?Lines:\s*(\d+)\].*?(\S+)',
                line
            )
            
            if match:
                results.append({
                    'status': int(match.group(1)),
                    'size': int(match.group(2)),
                    'words': int(match.group(3)),
                    'lines': int(match.group(4)),
                    'url': match.group(5) if len(match.groups()) > 4 else ''
                })
        
        return {
            'tool': 'ffuf',
            'total_results': len(results),
            'results': results
        }


class WfuzzParser:
    """Parser para resultados de Wfuzz."""
    
    @staticmethod
    def parse_output(output: str) -> Dict[str, Any]:
        """
        Parsea la salida de Wfuzz.
        
        Formato típico:
        000000001:   200        123 L    456 W    7890 Ch     "admin"
        """
        results = []
        
        for line in output.split('\n'):
            # Buscar líneas con resultados
            match = re.match(
                r'(\d+):\s+(\d+)\s+(\d+)\s+L\s+(\d+)\s+W\s+(\d+)\s+Ch\s+"([^"]+)"',
                line.strip()
            )
            
            if match:
                results.append({
                    'id': match.group(1),
                    'status': int(match.group(2)),
                    'lines': int(match.group(3)),
                    'words': int(match.group(4)),
                    'chars': int(match.group(5)),
                    'payload': match.group(6)
                })
        
        # Filtrar por status interesante
        interesting = [
            r for r in results
            if r['status'] in [200, 201, 204, 301, 302, 401, 403, 500]
        ]
        
        return {
            'tool': 'wfuzz',
            'total_results': len(results),
            'interesting_results': len(interesting),
            'results': interesting[:100]  # Primeros 100
        }


class GraphQLParser:
    """Parser para análisis de GraphQL (introspection)."""
    
    @staticmethod
    def parse_introspection(json_str: str) -> Dict[str, Any]:
        """
        Parsea el resultado de introspection de GraphQL.
        """
        try:
            data = json.loads(json_str)
            
            schema = data.get('data', {}).get('__schema', {})
            
            # Extraer tipos
            types = schema.get('types', [])
            queries = []
            mutations = []
            
            # Buscar Query y Mutation types
            for type_def in types:
                if type_def.get('name') == 'Query':
                    queries = type_def.get('fields', [])
                elif type_def.get('name') == 'Mutation':
                    mutations = type_def.get('fields', [])
            
            # Extraer custom types (excluir built-in)
            custom_types = [
                t for t in types
                if not t.get('name', '').startswith('__')
                and t.get('kind') == 'OBJECT'
                and t.get('name') not in ['Query', 'Mutation', 'Subscription']
            ]
            
            return {
                'tool': 'graphql',
                'introspection_enabled': True,
                'total_queries': len(queries),
                'total_mutations': len(mutations),
                'total_types': len(custom_types),
                'queries': [q.get('name') for q in queries[:50]],
                'mutations': [m.get('name') for m in mutations[:50]],
                'custom_types': [t.get('name') for t in custom_types[:50]],
                'sensitive_fields': GraphQLParser._find_sensitive_fields(types)
            }
            
        except json.JSONDecodeError:
            return {
                'tool': 'graphql',
                'error': 'Failed to parse GraphQL introspection response'
            }
    
    @staticmethod
    def _find_sensitive_fields(types: List[Dict]) -> List[str]:
        """Busca campos potencialmente sensibles."""
        sensitive_keywords = [
            'password', 'secret', 'token', 'api_key', 'apikey',
            'private', 'ssn', 'credit_card', 'auth'
        ]
        
        sensitive_fields = []
        
        for type_def in types:
            type_name = type_def.get('name', '')
            fields = type_def.get('fields', [])
            
            for field in fields:
                field_name = field.get('name', '').lower()
                
                for keyword in sensitive_keywords:
                    if keyword in field_name:
                        sensitive_fields.append(f'{type_name}.{field.get("name")}')
                        break
        
        return sensitive_fields[:20]  # Top 20


class PostmanParser:
    """Parser para colecciones de Postman/Newman."""
    
    @staticmethod
    def parse_collection(json_str: str) -> Dict[str, Any]:
        """
        Parsea una colección de Postman.
        """
        try:
            collection = json.loads(json_str)
            
            info = collection.get('info', {})
            items = collection.get('item', [])
            
            # Contar requests por método
            methods = {}
            total_requests = 0
            
            def count_requests(item_list):
                nonlocal total_requests
                count = 0
                for item in item_list:
                    if 'request' in item:
                        count += 1
                        total_requests += 1
                        method = item.get('request', {}).get('method', 'GET')
                        methods[method] = methods.get(method, 0) + 1
                    if 'item' in item:
                        count += count_requests(item['item'])
                return count
            
            count_requests(items)
            
            return {
                'tool': 'postman',
                'collection_name': info.get('name'),
                'collection_id': info.get('_postman_id'),
                'total_requests': total_requests,
                'methods': methods,
                'has_auth': 'auth' in collection,
                'has_variables': 'variable' in collection
            }
            
        except json.JSONDecodeError:
            return {
                'tool': 'postman',
                'error': 'Failed to parse Postman collection'
            }
    
    @staticmethod
    def parse_newman_output(json_str: str) -> Dict[str, Any]:
        """
        Parsea el resultado de Newman (CLI de Postman).
        """
        try:
            data = json.loads(json_str)
            
            run = data.get('run', {})
            stats = run.get('stats', {})
            
            return {
                'tool': 'newman',
                'collection': run.get('collection', {}).get('name'),
                'total_requests': stats.get('requests', {}).get('total', 0),
                'failed_requests': stats.get('requests', {}).get('failed', 0),
                'total_assertions': stats.get('assertions', {}).get('total', 0),
                'failed_assertions': stats.get('assertions', {}).get('failed', 0),
                'execution_time': stats.get('timings', {}).get('completed', 0),
                'success_rate': (
                    (stats.get('requests', {}).get('total', 0) - 
                     stats.get('requests', {}).get('failed', 0)) / 
                    max(stats.get('requests', {}).get('total', 1), 1) * 100
                )
            }
            
        except json.JSONDecodeError:
            return {
                'tool': 'newman',
                'error': 'Failed to parse Newman output'
            }

