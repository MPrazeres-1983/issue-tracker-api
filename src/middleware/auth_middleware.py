"""Authentication and authorization middleware."""

from functools import wraps
from typing import Callable, List, Optional
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from src.utils.responses import unauthorized_response, forbidden_response
from src.utils.logger import logger


def jwt_required_custom(fn: Callable) -> Callable:
    """
    Custom JWT required decorator with better error handling.
    
    Args:
        fn: Function to decorate
    
    Returns:
        Decorated function
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            return unauthorized_response("Invalid or missing authentication token")

        # JWTs remain valid until expiry, so re-check the user's current state.
        from src.repositories import UserRepository
        identity = get_jwt_identity()
        user = UserRepository().get_by_id(identity.get('user_id'))
        if user is None or not user.is_active:
            return unauthorized_response("Account disabled or no longer exists")

        # Do not turn unrelated business errors into misleading HTTP 401.
        return fn(*args, **kwargs)
    
    return wrapper


def require_auth(fn: Callable) -> Callable:
    """
    Decorator to require authentication.
    
    Args:
        fn: Function to decorate
    
    Returns:
        Decorated function
    """
    return jwt_required_custom(fn)


def require_role(*allowed_roles: str) -> Callable:
    """
    Decorator to require specific user role(s).
    
    Args:
        allowed_roles: Allowed role names
    
    Returns:
        Decorator function
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        @jwt_required_custom
        def wrapper(*args, **kwargs):
            try:
                identity = get_jwt_identity()
                from src.repositories import UserRepository
                user = UserRepository().get_by_id(identity.get('user_id'))
                if user is None or not user.is_active:
                    return unauthorized_response("Account disabled or no longer exists")
                user_role = user.role
                
                if user_role not in allowed_roles:
                    logger.warning(f"Access denied for role {user_role}. Required: {allowed_roles}")
                    return forbidden_response(f"Access denied. Required role: {', '.join(allowed_roles)}")
                
                return fn(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in role check: {str(e)}")
                return forbidden_response("Authorization failed")
        
        return wrapper
    return decorator


def get_current_user_id() -> Optional[int]:
    """
    Get current authenticated user ID from JWT.
    
    Returns:
        User ID or None
    """
    try:
        identity = get_jwt_identity()
        return identity.get('user_id')
    except Exception:
        return None


def get_current_user_identity() -> Optional[dict]:
    """
    Get current authenticated user identity from JWT.
    
    Returns:
        User identity dict or None
    """
    try:
        return get_jwt_identity()
    except Exception:
        return None


def get_current_user_role() -> Optional[str]:
    """
    Get current authenticated user role from JWT.
    
    Returns:
        User role or None
    """
    try:
        identity = get_jwt_identity()
        return identity.get('role')
    except Exception:
        return None


def optional_auth(fn: Callable) -> Callable:
    """
    Decorator for optional authentication.
    Endpoint works with or without auth, but provides user info if authenticated.
    
    Args:
        fn: Function to decorate
    
    Returns:
        Decorated function
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
        except Exception:
            pass  # Authentication is optional
        
        return fn(*args, **kwargs)
    
    return wrapper
