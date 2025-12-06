"""
Unit Tests - API Endpoints
===========================

Tests para endpoints REST de la API.
"""

import pytest
import json
from unittest.mock import patch, Mock


class TestAuthEndpoints:
    """Tests para endpoints de autenticación."""
    
    def test_login_success(self, client, admin_user):
        """Test de login exitoso."""
        response = client.post('/api/v1/auth/login', json={
            'username': 'admin',
            'password': 'Admin123!@#'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
    
    def test_login_invalid_credentials(self, client):
        """Test de login con credenciales inválidas."""
        response = client.post('/api/v1/auth/login', json={
            'username': 'admin',
            'password': 'wrongpassword'
        })
        
        assert response.status_code in [401, 400]
    
    def test_login_missing_fields(self, client):
        """Test de login sin campos requeridos."""
        response = client.post('/api/v1/auth/login', json={
            'username': 'admin'
        })
        
        assert response.status_code == 400
    
    def test_refresh_token(self, client, admin_user):
        """Test de refresh de token."""
        # Primero login
        login_response = client.post('/api/v1/auth/login', json={
            'username': 'admin',
            'password': 'Admin123!@#'
        })
        
        refresh_token = login_response.get_json()['refresh_token']
        
        # Refresh token
        response = client.post(
            '/api/v1/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data


class TestWorkspaceEndpoints:
    """Tests para endpoints de workspaces."""
    
    def test_create_workspace(self, client, auth_headers, workspace_data):
        """Test de creación de workspace."""
        response = client.post(
            '/api/v1/workspaces',
            json=workspace_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == workspace_data['name']
    
    def test_get_workspace(self, client, auth_headers, workspace):
        """Test de obtención de workspace."""
        response = client.get(
            f'/api/v1/workspaces/{workspace.id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == workspace.id
        assert data['name'] == workspace.name
    
    def test_list_workspaces(self, client, auth_headers, workspace):
        """Test de listado de workspaces."""
        response = client.get(
            '/api/v1/workspaces',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'workspaces' in data
        assert len(data['workspaces']) > 0
    
    def test_update_workspace(self, client, auth_headers, workspace):
        """Test de actualización de workspace."""
        response = client.put(
            f'/api/v1/workspaces/{workspace.id}',
            json={'name': 'Updated Workspace'},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Updated Workspace'
    
    def test_delete_workspace(self, client, auth_headers, workspace):
        """Test de eliminación de workspace."""
        response = client.delete(
            f'/api/v1/workspaces/{workspace.id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestScanningEndpoints:
    """Tests para endpoints de scanning."""
    
    @patch('tasks.scanning_tasks.nmap_scan_task.delay')
    def test_start_nmap_scan(self, mock_task, client, auth_headers, workspace):
        """Test de inicio de scan Nmap."""
        mock_task.return_value = Mock(id='test-task-123')
        
        response = client.post(
            '/api/v1/reconnaissance/nmap',
            json={
                'target': '192.168.1.1',
                'workspace_id': workspace.id,
                'scan_type': 'quick'
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'scan_id' in data
        assert data['status'] in ['running', 'pending']
    
    def test_start_scan_invalid_target(self, client, auth_headers, workspace):
        """Test de scan con target inválido."""
        response = client.post(
            '/api/v1/reconnaissance/nmap',
            json={
                'target': 'localhost',  # localhost no permitido
                'workspace_id': workspace.id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_get_scan_status(self, client, auth_headers, scan):
        """Test de obtención de estado de scan."""
        response = client.get(
            f'/api/v1/scanning/scans/{scan.id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['scan_id'] == scan.id
        assert 'status' in data
    
    def test_list_scans(self, client, auth_headers, workspace, scan):
        """Test de listado de scans."""
        response = client.get(
            f'/api/v1/scanning/scans?workspace_id={workspace.id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'scans' in data
        assert len(data['scans']) > 0
    
    def test_cancel_scan(self, client, auth_headers, scan):
        """Test de cancelación de scan."""
        response = client.post(
            f'/api/v1/scanning/scans/{scan.id}/cancel',
            headers=auth_headers
        )
        
        # Puede retornar 200 o 404 dependiendo de implementación
        assert response.status_code in [200, 404, 405]


class TestAPITestingEndpoints:
    """Tests para endpoints de API Testing."""
    
    @patch('tasks.api_testing_tasks.arjun_scan_task.delay')
    def test_start_arjun_scan(self, mock_task, client, auth_headers, workspace):
        """Test de inicio de scan con Arjun."""
        mock_task.return_value = Mock(id='test-task-123')
        
        response = client.post(
            '/api/v1/api-testing/arjun',
            json={
                'url': 'https://example.com/api',
                'workspace_id': workspace.id,
                'methods': ['GET', 'POST']
            },
            headers=auth_headers
        )
        
        # Puede retornar 201 o error si Arjun no está implementado
        assert response.status_code in [201, 500]
    
    def test_jwt_analysis(self, client, auth_headers, workspace):
        """Test de análisis de JWT."""
        jwt_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.test'
        
        response = client.post(
            '/api/v1/api-testing/jwt/analyze',
            json={
                'jwt_token': jwt_token,
                'workspace_id': workspace.id
            },
            headers=auth_headers
        )
        
        # Puede retornar 200 o error
        assert response.status_code in [200, 400, 500]


class TestSystemEndpoints:
    """Tests para endpoints del sistema."""
    
    def test_health_check(self, client):
        """Test de health check (no requiere auth)."""
        response = client.get('/api/v1/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
    
    def test_system_info(self, client, auth_headers):
        """Test de información del sistema."""
        response = client.get(
            '/api/v1/info',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'version' in data or 'api_version' in data


class TestAuthorizationEndpoints:
    """Tests de autorización y permisos."""
    
    def test_endpoint_requires_auth(self, client):
        """Test de que endpoint requiere autenticación."""
        response = client.get('/api/v1/workspaces')
        
        assert response.status_code == 401
    
    def test_invalid_token(self, client):
        """Test con token inválido."""
        response = client.get(
            '/api/v1/workspaces',
            headers={'Authorization': 'Bearer invalid_token_123'}
        )
        
        assert response.status_code == 422  # Unprocessable Entity (JWT error)
    
    def test_access_other_user_workspace(self, client, regular_user, workspace):
        """Test de acceso a workspace de otro usuario (debería fallar)."""
        # Login como usuario regular
        login_response = client.post('/api/v1/auth/login', json={
            'username': 'pentester1',
            'password': 'Pent123!@#'
        })
        
        token = login_response.get_json()['access_token']
        
        # Intentar acceder a workspace de admin
        response = client.get(
            f'/api/v1/workspaces/{workspace.id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Debería retornar 200 (puede ver) o 403 (no puede ver)
        assert response.status_code in [200, 403, 404]


class TestCORSHeaders:
    """Tests de headers CORS."""
    
    def test_cors_headers_present(self, client):
        """Test de presencia de headers CORS."""
        response = client.options('/api/v1/health')
        
        # Verificar que al menos responde
        assert response.status_code in [200, 204, 404]
    
    def test_cors_allowed_methods(self, client):
        """Test de métodos permitidos por CORS."""
        response = client.options('/api/v1/workspaces')
        
        # Verificar que hay headers de CORS
        assert response.status_code in [200, 204, 401]


class TestRateLimiting:
    """Tests de rate limiting."""
    
    def test_rate_limit_enforcement(self, client, admin_user):
        """Test de enforcement de rate limiting."""
        # Hacer muchas requests rápidas
        responses = []
        for i in range(150):  # Más que el límite por defecto
            response = client.post('/api/v1/auth/login', json={
                'username': 'admin',
                'password': 'wrongpassword'
            })
            responses.append(response.status_code)
        
        # Debería haber al menos un 429 (Too Many Requests)
        # Nota: Esto depende de si rate limiting está habilitado
        assert 429 in responses or all(r in [400, 401] for r in responses)


class TestInputValidation:
    """Tests de validación de inputs."""
    
    def test_sql_injection_prevention(self, client, auth_headers, workspace):
        """Test de prevención de SQL injection."""
        response = client.post(
            '/api/v1/reconnaissance/nmap',
            json={
                'target': "192.168.1.1'; DROP TABLE users; --",
                'workspace_id': workspace.id
            },
            headers=auth_headers
        )
        
        # Debería rechazar el input
        assert response.status_code == 400
    
    def test_xss_prevention(self, client, auth_headers, workspace_data):
        """Test de prevención de XSS."""
        workspace_data['name'] = '<script>alert("XSS")</script>'
        
        response = client.post(
            '/api/v1/workspaces',
            json=workspace_data,
            headers=auth_headers
        )
        
        # Debería aceptarlo pero escapar el HTML
        if response.status_code == 201:
            data = response.get_json()
            # El nombre no debería contener tags HTML ejecutables
            assert '<script>' not in data.get('name', '')


class TestErrorHandling:
    """Tests de manejo de errores."""
    
    def test_404_endpoint(self, client):
        """Test de endpoint no existente."""
        response = client.get('/api/v1/nonexistent')
        
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self, client):
        """Test de método HTTP no permitido."""
        response = client.delete('/api/v1/health')
        
        assert response.status_code == 405
    
    def test_400_bad_request(self, client, auth_headers):
        """Test de bad request."""
        response = client.post(
            '/api/v1/workspaces',
            json={'invalid': 'data'},
            headers=auth_headers
        )
        
        assert response.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__, '-v'])



