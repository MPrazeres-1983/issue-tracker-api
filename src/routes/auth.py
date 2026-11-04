"""Authentication routes."""

from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services import AuthService
from src.schemas import UserRegistrationSchema, UserLoginSchema, UserResponseSchema
from src.utils.responses import (
    success_response,
    error_response,
    validation_error_response,
    created_response,
)
from src.middleware import require_auth
from src.utils.logger import logger

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
auth_service = AuthService()


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request body:
        username: str
        email: str
        password: str
    
    Returns:
        201: User created
        400: Validation error or user already exists
    """
    try:
        # Validate input
        schema = UserRegistrationSchema()
        data = schema.load(request.get_json())
        
        # Register user
        user, error = auth_service.register(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        
        if error:
            return error_response(error, status_code=400)
        
        # Return user data
        user_schema = UserResponseSchema()
        return created_response(
            data=user_schema.dump(user),
            message="User registered successfully"
        )
    
    except ValidationError as e:
        return validation_error_response(e.messages)
    except Exception as e:
        logger.error(f"Error in register: {str(e)}")
        return error_response("Registration failed", status_code=500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user and generate tokens.
    
    Request body:
        username: str
        password: str
    
    Returns:
        200: Login successful with tokens
        400: Validation error
        401: Invalid credentials
    """
    try:
        # Validate input
        schema = UserLoginSchema()
        data = schema.load(request.get_json())
        
        # Authenticate user
        result, error = auth_service.login(
            username=data['username'],
            password=data['password']
        )
        
        if error:
            return error_response(error, status_code=401)
        
        return success_response(
            data=result,
            message="Login successful"
        )
    
    except ValidationError as e:
        return validation_error_response(e.messages)
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return error_response("Login failed", status_code=500)


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token.
    
    Returns:
        200: New access token
        401: Invalid or expired refresh token
    """
    try:
        identity = get_jwt_identity()
        
        # Generate new access token
        result, error = auth_service.refresh(identity)
        
        if error:
            return error_response(error, status_code=401)
        
        return success_response(
            data=result,
            message="Token refreshed successfully"
        )
    
    except Exception as e:
        logger.error(f"Error in refresh: {str(e)}")
        return error_response("Token refresh failed", status_code=500)


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """
    Logout user (client should discard tokens).
    
    Note: Since we're using JWT, actual logout is handled client-side
    by discarding the tokens. This endpoint is mainly for logging purposes.
    
    Returns:
        200: Logout successful
    """
    try:
        identity = get_jwt_identity()
        logger.info(f"User {identity['username']} logged out")
        
        return success_response(message="Logout successful")
    
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}")
        return error_response("Logout failed", status_code=500)


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """
    Get current authenticated user information.
    
    Returns:
        200: User information
        401: Unauthorized
        404: User not found
    """
    try:
        identity = get_jwt_identity()
        user_id = identity['user_id']
        
        user = auth_service.get_current_user(user_id)
        
        if not user:
            return error_response("User not found", status_code=404)
        
        user_schema = UserResponseSchema()
        return success_response(data=user_schema.dump(user))
    
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        return error_response("Failed to get user information", status_code=500)
