from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from .db import db
from .config import Config

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True)
    CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})

    # Configure file upload settings
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Optional: Limit the upload size to 16MB

    # Initialize extensions
    CORS(app)  # Allow all origins for API routes
    db.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    from .routes import api_bp
    from .auth import auth_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
