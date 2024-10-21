from flask import Blueprint, current_app, request, jsonify, make_response
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity, 
    unset_jwt_cookies, 
    decode_token
)
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from app.models import User
from app import db
from datetime import timedelta
import os
import re
import jwt

auth_bp = Blueprint('auth', __name__)

bcrypt = Bcrypt()

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def is_valid_email(email):
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.fullmatch(regex, email)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json  # Use JSON for other fields
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if 'profile_picture' not in request.files:
        return jsonify({"error": "Please upload a profile picture"}), 400

    profile_picture = request.files['profile_picture']

    if not profile_picture or not allowed_file(profile_picture.filename):
        return jsonify({"error": "Invalid file type. Allowed types: png, jpg, jpeg"}), 400

    if not username or not email or not password:
        return jsonify({"error": "Please provide all fields (username, email, password)"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    filename = secure_filename(profile_picture.filename)
    profile_picture_path = os.path.join(UPLOAD_FOLDER, filename)
    profile_picture.save(profile_picture_path)

    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        profile_picture=profile_picture_path
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error occurred during registration"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Please provide both email and password"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity={'id': user.id}, expires_delta=timedelta(minutes=30))
    refresh_token = create_refresh_token(identity={'id': user.id}, expires_delta=timedelta(days=7))

    response = make_response(jsonify({'access_token': access_token}), 200)
    response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', max_age=7*24*60*60)

    return response

@auth_bp.route('/auth/refresh', methods=['POST'])
def refresh_token():
    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        return jsonify({'error': 'Refresh token missing'}), 401

    try:
        decoded_refresh_token = decode_token(refresh_token)
        current_user = decoded_refresh_token['sub']

        new_access_token = create_access_token(identity=current_user, expires_delta=timedelta(minutes=30))

        return jsonify({'access_token': new_access_token}), 200
    except Exception as e:
        response = jsonify({"error": "Could not refresh access token"})
        response.delete_cookie('refresh_token')
        return response, 401

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({"message": "Successfully logged out"})
    response.delete_cookie('refresh_token')
    unset_jwt_cookies(response)
    return response, 200

# Updated validate-token route
@auth_bp.route('/validate-token', methods=['POST'])
def validate_token_route():
    token = request.json.get('token')

    if not token:
        return jsonify({"valid": False, "error": "Token is missing"}), 400

    try:
        # Verify the token using SECRET_KEY
        jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
        return jsonify({"valid": True}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"valid": False, "error": "Invalid token"}), 401

