"""Application factory and configuration."""

import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

from src.config import get_config
from src.models.base import db
from src.routes import register_blueprints
from src.middleware import register_error_handlers
from src.utils.logger import setup_logger, logger

# Load environment variables
load_dotenv()


def create_app(config_name: str = None) -> Flask:
    """
    Application factory pattern.
    
    Args:
        config_name: Configuration name (development, testing, production)
    
    Returns:
        Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Setup logging
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_format = app.config.get('LOG_FORMAT', 'json')
    setup_logger('issue_tracker', log_level, log_format)
    
    logger.info(f"Starting application in {config_name} mode")
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Register blueprints
    register_blueprints(app)

    # A useful public landing endpoint that checks database readiness.
    # Render's default GET / no longer returns 404 for a healthy API.
    from src.routes.health import health_check
    app.add_url_rule('/', endpoint='root_health', view_func=health_check)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add request/response hooks
    register_hooks(app)
    
    logger.info("Application initialized successfully")
    
    return app


def initialize_extensions(app: Flask) -> None:
    """
    Initialize Flask extensions.
    
    Args:
        app: Flask application instance
    """
    # Database
    db.init_app(app)
    
    # JWT
    jwt = JWTManager(app)
    
    # CORS
    cors_origins = app.config['CORS_ORIGINS']
    if cors_origins == "*":
        CORS(app)
    else:
        origins = [origin.strip() for origin in cors_origins.split(",")]
        CORS(
            app,
            origins=origins,
            methods=app.config.get('CORS_METHODS', ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']),
            allow_headers=app.config.get('CORS_ALLOW_HEADERS', ['Content-Type', 'Authorization']),
            supports_credentials=app.config.get('CORS_SUPPORTS_CREDENTIALS', True)
        )
    
    # Rate limiting
    if app.config.get('RATELIMIT_ENABLED', True):
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=[app.config.get('RATELIMIT_DEFAULT', '100 per minute')],
            storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://'),
            headers_enabled=app.config.get('RATELIMIT_HEADERS_ENABLED', True)
        )
        
        # Store limiter in app for access in routes if needed
        app.limiter = limiter
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        from src.utils.responses import error_response
        return error_response(
            message="Token has expired",
            status_code=401,
            error_code="TOKEN_EXPIRED"
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        from src.utils.responses import error_response
        return error_response(
            message="Invalid token",
            status_code=401,
            error_code="INVALID_TOKEN"
        )
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        from src.utils.responses import error_response
        return error_response(
            message="Missing authorization token",
            status_code=401,
            error_code="MISSING_TOKEN"
        )
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        from src.utils.responses import error_response
        return error_response(
            message="Token has been revoked",
            status_code=401,
            error_code="TOKEN_REVOKED"
        )
    
    logger.info("Extensions initialized")


def register_hooks(app: Flask) -> None:
    """
    Register request/response hooks.
    
    Args:
        app: Flask application instance
    """
    @app.before_request
    def before_request():
        """Log incoming requests."""
        from flask import request
        logger.debug(f"{request.method} {request.path}")
    
    @app.after_request
    def after_request(response):
        """Add custom headers to response."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    logger.info("Request/response hooks registered")


# Create CLI commands
def create_cli_commands(app: Flask) -> None:
    """
    Create CLI commands for the application.
    
    Args:
        app: Flask application instance
    """
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        with app.app_context():
            db.create_all()
            logger.info("Database initialized")
            print("Database initialized successfully")
    
    @app.cli.command()
    def drop_db():
        """Drop all database tables."""
        with app.app_context():
            if input("Are you sure you want to drop all tables? (yes/no): ").lower() == 'yes':
                db.drop_all()
                logger.info("Database dropped")
                print("Database dropped successfully")
            else:
                print("Operation cancelled")
    
    @app.cli.command()
    def create_admin():
        """Create an admin user."""
        from src.services import AuthService
        
        with app.app_context():
            auth_service = AuthService()
            
            username = input("Admin username: ")
            email = input("Admin email: ")
            password = input("Admin password: ")
            
            user, error = auth_service.register(
                username=username,
                email=email,
                password=password,
                role='admin'
            )
            
            if error:
                print(f"Error: {error}")
            else:
                print(f"Admin user '{username}' created successfully")


# For development
if __name__ == '__main__':
    app = create_app()
    create_cli_commands(app)
    app.run(debug=True, host='0.0.0.0', port=5000)
