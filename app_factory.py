import os
from flask import Flask
from dotenv import load_dotenv
from flask_mail import Mail

from extensions import db, migrate, session as session_ext, csrf
from routes.__init__ import register_routes

def init_app():
    """Initialize the Flask application and configurations."""
    # Configure application
    load_dotenv() #Load variables from .env
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    # Verify if secret key is correctly loaded
    if not app.secret_key:
        raise ValueError("No SECRET_KEY found in environment")

    # Set upload folder
    UPLOAD_FOLDER = 'static/uploads'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['UPLOADED_PHOTOS_DEST'] = app.config['UPLOAD_FOLDER']
    app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024  # Max size: 6MB

    # Configurations
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///petpal.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    session_ext.init_app(app)
    csrf.init_app(app)

    # Configure Flask-Mail: ALL settings are pulled from environment variables (your .env file)
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    # Use Python's bool conversion for MAIL_USE_TLS (since os.getenv returns a string)
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'False').lower() in ('true', '1', 't')
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() in ('true', '1', 't')

    # CRITICAL FIX: Ensure the default sender is read
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    mail = Mail(app)

    # Register blueprints inside app context
    with app.app_context():
        register_routes(app)  # Register all blueprints from routes/__init__.py

    @app.after_request
    def after_request(response):
        """Ensure responses aren't cached"""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    return app
