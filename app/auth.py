from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    create_refresh_token,
)
import jwt
from flask_cors import CORS
from datetime import timedelta
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from .models import User
from .db import db
import os

auth_bp = Blueprint('auth', __name__)
CORS(auth_bp, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:8080"}})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        # Generate access and refresh tokens
        access_token = create_access_token(identity={'id': user.id}, expires_delta=timedelta(minutes=15))
        refresh_token = create_refresh_token(identity={'id': user.id}, expires_delta=timedelta(days=7))  # Fixed: removed comma
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
    return jsonify(message="Invalid credentials"), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing required fields"}), 400

    hashed_password = generate_password_hash(data['password'])
    
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully!"}), 201

@auth_bp.route('/profile-picture', methods=['POST'])
@jwt_required()
def upload_profile_picture():
    user_id = get_jwt_identity()['id']
    
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    file.save(filepath)

    user = User.query.get(user_id)
    user.profile_picture = filepath
    db.session.commit()

    return jsonify({"message": "Profile picture uploaded", "file_path": filepath}), 200

@auth_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_user():
    user_id = get_jwt_identity()['id']
    data = request.get_json()

    user = User.query.get(user_id)

    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']

    db.session.commit()
    return jsonify({"message": "User information updated"}), 200

@auth_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()['id']

    user = User.query.get(user_id)

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "Account deleted"}), 200

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({'error': 'Missing refresh token'}), 400

    try:
        payload = jwt.decode(refresh_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])

        # Create a new access token
        new_access_token = create_access_token(identity={'id': payload['identity']['id']})

        return jsonify({'new_access_token': new_access_token}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Refresh token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid refresh token'}), 401