import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .db import db
from .config import Config

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Corrected CORS configuration: Dictionary with resource paths as keys
    CORS(app, resources={
        r"/auth/*": {"origins": "http://localhost:8080"},
        r"/api/*": {"origins": "http://localhost:8080"}
    },
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"])

    # Configure file upload settings
    upload_folder = os.path.join(app.root_path, 'static/uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    from .routes import api_bp
    from .auth import auth_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
