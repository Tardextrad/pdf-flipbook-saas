import os
import logging
import secrets
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration
    configure_app(app)
    configure_uploads(app)
    configure_cors(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints and initialize database
    with app.app_context():
        register_blueprints(app)
        init_database(app)
    
    return app

def configure_app(app):
    """Set core application configuration."""
    # Get required environment variables
    required_vars = ['DATABASE_URL', 'FLASK_SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Set Flask configuration
    app.config.update(
        SECRET_KEY=os.environ['FLASK_SECRET_KEY'],
        SQLALCHEMY_DATABASE_URI=os.environ['DATABASE_URL'],
        SQLALCHEMY_ENGINE_OPTIONS={
            "pool_recycle": 300,
            "pool_pre_ping": True,
        },
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
        LOGIN_DISABLED=False  # Enable login functionality
    )
    logger.info("Application configured successfully")

def configure_uploads(app):
    """Configure upload directory."""
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.config['UPLOAD_FOLDER'] = os.path.join(static_folder, 'uploads')
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        logger.info(f"Created upload folder at {app.config['UPLOAD_FOLDER']}")

def configure_cors(app):
    """Configure CORS settings."""
    CORS(app, 
         resources={
             r"/*": {
                 "origins": [
                     "https://*.replit.app",
                     "https://*.repl.co",
                     "http://localhost:3000",
                     "http://localhost:5000",
                     "http://localhost:8080",
                     "http://0.0.0.0:8080"
                 ],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization", 
                                "X-Requested-With", "Accept", "Origin"],
                 "supports_credentials": True,
                 "expose_headers": ["Content-Range", "X-Content-Range"]
             }
         })
    logger.info("CORS configured")

def init_extensions(app):
    """Initialize Flask extensions."""
    db.init_app(app)
    login_manager.init_app(app)
    # Set login view after init_app to avoid the type error
    app.config['LOGIN_VIEW'] = 'login'
    login_manager.login_view = app.config['LOGIN_VIEW']
    login_manager.session_protection = 'strong'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    logger.info("Extensions initialized")

def register_blueprints(app):
    """Register Flask blueprints."""
    # Import blueprints here to avoid circular imports
    from api import api
    app.register_blueprint(api, url_prefix='/api')

    # Import routes after creating app instance
    from main import init_routes
    init_routes(app)
    logger.info("Blueprints and routes registered")

def init_database(app):
    """Initialize the database."""
    # Import models here to avoid circular imports
    import models
    db.create_all()
    logger.info("Database initialized successfully")
