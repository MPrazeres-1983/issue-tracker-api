"""Integration tests for auth routes."""

import pytest
import json


@pytest.mark.integration
class TestAuthRoutes:
    """Test cases for authentication routes."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/v1/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'NewPass123!'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'data' in data
        assert data['data']['username'] == 'newuser'
        assert data['data']['email'] == 'new@example.com'
    
    @pytest.mark.parametrize('requested_role', ['admin', 'viewer', 'developer'])
    def test_public_registration_rejects_client_supplied_role(self, client, requested_role):
        """Public clients must not be able to select their own permissions."""
        response = client.post('/api/v1/auth/register', json={
            'username': 'role_probe',
            'email': 'roleprobe@example.com',
            'password': 'NewPass123!',
            'role': requested_role,
        })

        assert response.status_code == 422
        from src.repositories import UserRepository
        assert UserRepository().get_by_username('role_probe') is None

    def test_public_registration_assigns_least_privilege(self, client):
        response = client.post('/api/v1/auth/register', json={
            'username': 'normaluser',
            'email': 'normaluser@example.com',
            'password': 'NewPass123!',
        })
        assert response.status_code == 201
        assert response.get_json()['data']['role'] == 'developer'

    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post('/api/v1/auth/register', json={
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'NewPass123!'
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert 'error' in data
    
    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post('/api/v1/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'weak'
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert 'error' in data
    
    def test_login_success(self, client, sample_user):
        """Test successful login."""
        response = client.post('/api/v1/auth/login', json={
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
        assert data['data']['user']['username'] == 'testuser'
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/api/v1/auth/login', json={
            'username': 'nonexistent',
            'password': 'WrongPass123!'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user information."""
        response = client.get('/api/v1/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert data['data']['username'] == 'testuser'
    
    def test_get_current_user_no_auth(self, client):
        """Test getting current user without authentication."""
        response = client.get('/api/v1/auth/me')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_logout(self, client, auth_headers):
        """Test logout."""
        response = client.post('/api/v1/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Logout successful'
