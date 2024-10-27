import os
import logging
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
    
    # Register blueprints
    register_blueprints(app)
    
    # Initialize database
    init_database(app)
    
    return app

def configure_app(app):
    """Set core application configuration."""
    app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL"),
        SQLALCHEMY_ENGINE_OPTIONS={
            "pool_recycle": 300,
            "pool_pre_ping": True,
        },
        MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
    )
    logger.info("Application configured")

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
    login_manager.login_view = 'login'  # String value instead of "login"
    logger.info("Extensions initialized")

def register_blueprints(app):
    """Register Flask blueprints."""
    from api import api
    app.register_blueprint(api, url_prefix='/api')
    logger.info("Blueprints registered")

def init_database(app):
    """Initialize the database."""
    try:
        with app.app_context():
            import models  # Import models here to avoid circular imports
            db.create_all()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

# Create the application instance
app = create_app()

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', '').lower() == 'true'  # Convert string to boolean
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
