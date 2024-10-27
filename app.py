import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

app = Flask(__name__)

# Environment variables and configuration
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Set up upload folder in static directory
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app.config['UPLOAD_FOLDER'] = os.path.join(static_folder, 'uploads')

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Configure CORS with specific origins
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
             "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
             "supports_credentials": True,
             "expose_headers": ["Content-Range", "X-Content-Range"]
         }
     })

# Initialize extensions with app context
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"

# Initialize database
with app.app_context():
    import models
    db.create_all()
    logger.info("Database initialized successfully")
