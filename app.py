import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from flask_cors import CORS

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

app = Flask(__name__)

# Configure CORS with more flexible settings
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",           # Next.js development server
            "http://localhost:5000",           # Flask development server
            "https://*.replit.app",            # Replit deployment domains
            "https://*.repl.co"                # Additional Replit domains
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "Access-Control-Allow-Credentials",
            "X-Requested-With"
        ],
        "supports_credentials": True,          # Allow credentials
        "expose_headers": ["Content-Range", "X-Total-Count"],
        "max_age": 600                         # Cache preflight requests for 10 minutes
    }
})

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

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"  # Use string literal for view function name

with app.app_context():
    import models
    db.create_all()
