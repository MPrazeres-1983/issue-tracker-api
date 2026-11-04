"""Integration tests for health check routes."""

import pytest


@pytest.mark.integration
class TestHealthRoutes:
    """Test cases for health check routes."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/v1/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert data['data']['status'] == 'healthy'
        assert data['data']['database'] == 'healthy'
    
    def test_root_health_checks_database(self, client):
        response = client.get('/')
        assert response.status_code == 200
        body = response.get_json()
        assert body['data']['database'] == 'healthy'

    def test_ping(self, client):
        """Test ping endpoint."""
        response = client.get('/api/v1/ping')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert data['data']['message'] == 'pong'
