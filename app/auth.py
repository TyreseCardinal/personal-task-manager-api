from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from .models import User
from .db import db
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login and return a JWT token."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):  # Ensure `check_password` is implemented
        access_token = create_access_token(identity={'id': user.id})
        return jsonify(access_token=access_token), 200
    
    return jsonify(message="Invalid credentials"), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing required fields"}), 400

    hashed_password = generate_password_hash(data['password'])
    
    # Create a new user
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
    """Upload a profile picture for the authenticated user."""
    user_id = get_jwt_identity()['id']
    
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400

    # Secure the filename
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    # Save the file to the upload folder
    file.save(filepath)

    # Update user profile picture path in the database
    user = User.query.get(user_id)
    user.profile_picture = filepath
    db.session.commit()

    return jsonify({"message": "Profile picture uploaded", "file_path": filepath}), 200

@auth_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_user():
    """Update the authenticated user's information."""
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
    """Delete the authenticated user's account."""
    user_id = get_jwt_identity()['id']

    user = User.query.get(user_id)

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "Account deleted"}), 200
