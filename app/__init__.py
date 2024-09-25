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
    
    # Configure CORS to allow credentials and requests from localhost:8080 only
    CORS(app, supports_credentials=True, origins=["http://localhost:8080"])
    
    # Configure file upload settings
    upload_folder = os.path.join(app.root_path, 'static/uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    app.config['UPLOAD_FOLDER'] = 'static'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Optional: Limit the upload size to 16MB
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    from .routes import api_bp
    from .auth import auth_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
