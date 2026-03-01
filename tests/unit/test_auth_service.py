"""Unit tests for AuthService."""

import pytest
from src.services import AuthService
from unittest.mock import MagicMock, patch


@pytest.mark.unit
class TestAuthService:
    """Test cases for AuthService."""
    
    def test_hash_password(self):
        """Test password hashing."""
        auth_service = AuthService()
        password = 'TestPassword123!'
        
        hashed = auth_service.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert auth_service.verify_password(password, hashed)
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        auth_service = AuthService()
        password = 'TestPassword123!'
        hashed = auth_service.hash_password(password)
        
        result = auth_service.verify_password(password, hashed)
        
        assert result is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        auth_service = AuthService()
        password = 'TestPassword123!'
        hashed = auth_service.hash_password(password)
        
        result = auth_service.verify_password('WrongPassword', hashed)
        
        assert result is False
    
    def test_register_success(self, db):
        """Test successful user registration."""
        auth_service = AuthService()
        
        user, error = auth_service.register(
            username='newuser',
            email='new@example.com',
            password='NewPass123!',
            role='developer'
        )
        
        assert user is not None, f"Erro interno da API: {error}"
        assert error is None
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.role == 'developer'
        assert user.is_active is True
    
    def test_register_duplicate_username(self, db, sample_user):
        """Test registration with duplicate username."""
        auth_service = AuthService()
        
        user, error = auth_service.register(
            username='testuser',  # Already exists
            email='another@example.com',
            password='NewPass123!',
            role='developer'
        )
        
        assert user is None
        assert error == "Username already exists"
    
    def test_register_duplicate_email(self, db, sample_user):
        """Test registration with duplicate email."""
        auth_service = AuthService()
        
        user, error = auth_service.register(
            username='anotheruser',
            email='test@example.com',  # Already exists
            password='NewPass123!',
            role='developer'
        )
        
        assert user is None
        assert error == "Email already exists"
    
    def test_login_success(self, db, sample_user):
        """Test successful login."""
        auth_service = AuthService()
        
        result, error = auth_service.login(
            username='testuser',
            password='TestPass123!'
        )
        
        assert result is not None
        assert error is None
        assert 'access_token' in result
        assert 'refresh_token' in result
        assert result['token_type'] == 'Bearer'
        assert result['user']['username'] == 'testuser'
    
    def test_login_invalid_username(self, db):
        """Test login with invalid username."""
        auth_service = AuthService()
        
        result, error = auth_service.login(
            username='nonexistent',
            password='SomePassword123!'
        )
        
        assert result is None
        assert error == "Invalid credentials"
    
    def test_login_invalid_password(self, db, sample_user):
        """Test login with invalid password."""
        auth_service = AuthService()
        
        result, error = auth_service.login(
            username='testuser',
            password='WrongPassword123!'
        )
        
        assert result is None
        assert error == "Invalid credentials"
