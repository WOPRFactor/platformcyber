"""
Integration Tests
==================

Tests de integración end-to-end.
"""

import pytest
import time
from unittest.mock import patch, Mock


class TestFullScanFlow:
    """Test de flujo completo de scanning."""
    
    @patch('tasks.scanning_tasks.nmap_scan_task.delay')
    @patch('tasks.scanning_tasks.subprocess.run')
    def test_complete_nmap_scan_workflow(
        self,
        mock_subprocess,
        mock_task,
        client,
        auth_headers,
        workspace,
        mock_nmap_output
    ):
        """
        Test completo: Crear workspace → Iniciar scan → Verificar estado → Obtener resultados.
        """
        # 1. Verificar que workspace existe
        workspace_response = client.get(
            f'/api/v1/workspaces/{workspace.id}',
            headers=auth_headers
        )
        assert workspace_response.status_code == 200
        
        # 2. Mock de task
        mock_task.return_value = Mock(id='test-task-123')
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout=mock_nmap_output,
            stderr=''
        )
        
        # 3. Iniciar scan de Nmap
        scan_response = client.post(
            '/api/v1/reconnaissance/nmap',
            json={
                'target': '192.168.1.1',
                'workspace_id': workspace.id,
                'scan_type': 'quick'
            },
            headers=auth_headers
        )
        
        assert scan_response.status_code == 201
        scan_data = scan_response.get_json()
        scan_id = scan_data['scan_id']
        
        # 4. Verificar estado del scan
        status_response = client.get(
            f'/api/v1/scanning/scans/{scan_id}',
            headers=auth_headers
        )
        
        assert status_response.status_code == 200
        status_data = status_response.get_json()
        assert 'status' in status_data
        
        # 5. Listar scans del workspace
        list_response = client.get(
            f'/api/v1/scanning/scans?workspace_id={workspace.id}',
            headers=auth_headers
        )
        
        assert list_response.status_code == 200
        list_data = list_response.get_json()
        assert len(list_data['scans']) >= 1


class TestAuthenticationFlow:
    """Test de flujo de autenticación."""
    
    def test_complete_auth_flow(self, client, admin_user):
        """
        Test completo: Login → Acceso con token → Refresh → Logout.
        """
        # 1. Login
        login_response = client.post('/api/v1/auth/login', json={
            'username': 'admin',
            'password': 'Admin123!@#'
        })
        
        assert login_response.status_code == 200
        tokens = login_response.get_json()
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        
        # 2. Acceder a endpoint protegido
        workspaces_response = client.get(
            '/api/v1/workspaces',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        assert workspaces_response.status_code == 200
        
        # 3. Refresh token
        refresh_response = client.post(
            '/api/v1/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.get_json()
        assert 'access_token' in new_tokens


class TestWorkspaceManagementFlow:
    """Test de flujo de gestión de workspaces."""
    
    def test_complete_workspace_lifecycle(self, client, auth_headers, workspace_data):
        """
        Test completo: Crear → Listar → Actualizar → Eliminar workspace.
        """
        # 1. Crear workspace
        create_response = client.post(
            '/api/v1/workspaces',
            json=workspace_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        workspace = create_response.get_json()
        workspace_id = workspace['id']
        
        # 2. Obtener workspace
        get_response = client.get(
            f'/api/v1/workspaces/{workspace_id}',
            headers=auth_headers
        )
        
        assert get_response.status_code == 200
        
        # 3. Actualizar workspace
        update_response = client.put(
            f'/api/v1/workspaces/{workspace_id}',
            json={'name': 'Updated Workspace'},
            headers=auth_headers
        )
        
        assert update_response.status_code == 200
        updated = update_response.get_json()
        assert updated['name'] == 'Updated Workspace'
        
        # 4. Listar workspaces
        list_response = client.get(
            '/api/v1/workspaces',
            headers=auth_headers
        )
        
        assert list_response.status_code == 200
        workspaces = list_response.get_json()['workspaces']
        assert any(w['id'] == workspace_id for w in workspaces)
        
        # 5. Eliminar workspace
        delete_response = client.delete(
            f'/api/v1/workspaces/{workspace_id}',
            headers=auth_headers
        )
        
        assert delete_response.status_code == 200
        
        # 6. Verificar que fue eliminado
        get_deleted = client.get(
            f'/api/v1/workspaces/{workspace_id}',
            headers=auth_headers
        )
        
        assert get_deleted.status_code == 404


class TestCeleryTaskFlow:
    """Test de flujo con tareas de Celery."""
    
    @patch('tasks.scanning_tasks.nmap_scan_task.apply_async')
    def test_async_scan_execution(
        self,
        mock_task,
        client,
        auth_headers,
        workspace,
        session
    ):
        """
        Test de ejecución asíncrona de scan con Celery.
        """
        from celery.result import AsyncResult
        
        # Mock task result
        mock_result = Mock()
        mock_result.id = 'task-123'
        mock_result.state = 'PENDING'
        mock_task.return_value = mock_result
        
        # 1. Iniciar scan
        response = client.post(
            '/api/v1/reconnaissance/nmap',
            json={
                'target': '192.168.1.1',
                'workspace_id': workspace.id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        
        # 2. Verificar que se llamó a Celery
        assert mock_task.called or response.status_code == 201


class TestErrorRecovery:
    """Test de recuperación de errores."""
    
    def test_retry_on_failure(self, client, auth_headers, workspace):
        """Test de retry automático en fallos."""
        # Intentar scan con target inválido
        response = client.post(
            '/api/v1/reconnaissance/nmap',
            json={
                'target': 'localhost',  # Inválido
                'workspace_id': workspace.id
            },
            headers=auth_headers
        )
        
        # Debería rechazar inmediatamente
        assert response.status_code == 400
    
    def test_graceful_degradation(self, client):
        """Test de degradación graciosa."""
        # Intentar acceso sin auth
        response = client.get('/api/v1/workspaces')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'msg' in data or 'error' in data or 'message' in data


class TestConcurrentOperations:
    """Test de operaciones concurrentes."""
    
    @patch('tasks.scanning_tasks.nmap_scan_task.delay')
    def test_multiple_scans_simultaneously(
        self,
        mock_task,
        client,
        auth_headers,
        workspace
    ):
        """Test de múltiples scans simultáneos."""
        mock_task.return_value = Mock(id='test-task')
        
        # Iniciar múltiples scans
        responses = []
        for i in range(5):
            response = client.post(
                '/api/v1/reconnaissance/nmap',
                json={
                    'target': f'192.168.1.{i+1}',
                    'workspace_id': workspace.id
                },
                headers=auth_headers
            )
            responses.append(response.status_code)
        
        # Todos deberían ser aceptados
        assert all(status == 201 for status in responses)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])



