import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
from .db import db
from werkzeug.utils import secure_filename

api_bp = Blueprint('api', __name__)

@api_bp.route('/<path:path>', methods=['OPTIONS'])
def handle_preflight(path):
    return jsonify({'status': 'ok'}), 200

@api_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """Retrieve all tasks for the authenticated user."""
    from .models import Task  # Local import to avoid circular dependency
    current_user = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=current_user['id']).all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'completed': t.completed,
        'created_at': t.created_at,
        'updated_at': t.updated_at
    } for t in tasks]), 200

@api_bp.route('/task/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Retrieve a specific task by ID for the authenticated user."""
    from .models import Task  # Local import to avoid circular dependency
    task = Task.query.get(task_id)
    if task and task.user_id == get_jwt_identity()['id']:
        return jsonify({
            'id': task.id,
            'title': task.title, 
            'completed': task.completed,
            'created_at': task.created_at,
            'updated_at': task.updated_at
        }), 200
    return jsonify(message="Task not found"), 404

@api_bp.route('/task', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task for the authenticated user."""
    from .models import Task  # Local import to avoid circular dependency
    data = request.get_json()
    current_user = get_jwt_identity()

    new_task = Task(
        title=data['title'],
        completed=data.get('completed', False),
        user_id=current_user['id']
    )
    db.session.add(new_task)
    db.session.commit()
    
    return jsonify(message="Task created", task_id=new_task.id), 201

@api_bp.route('/task/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a specific task by ID for the authenticated user."""
    from .models import Task  # Local import to avoid circular dependency
    task = Task.query.get(task_id)
    if task and task.user_id == get_jwt_identity()['id']:
        data = request.get_json()
        task.title = data.get('title', task.title)
        task.completed = data.get('completed', task.completed)
        db.session.commit()
        return jsonify(message="Task updated"), 200
    return jsonify(message="Task not found or unauthorized"), 404

@api_bp.route('/task/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a specific task by ID for the authenticated user."""
    from .models import Task  # Local import to avoid circular dependency
    task = Task.query.get(task_id)
    if task and task.user_id == get_jwt_identity()['id']:
        db.session.delete(task)
        db.session.commit()
        return jsonify(message="Task deleted"), 200
    return jsonify(message="Task not found or unauthorized"), 404

@api_bp.route('/user', methods=['PUT'])
@jwt_required()
def update_user_info():
    """ Update user information for the authenticated user """
    from .models import User
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user['id']).first()
    
    if not user:
        return jsonify(message="User not found"), 404
    
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    
    db.session.commit()
    return jsonify(message="User info updated successfully"), 200

@api_bp.route('/user', methods=['DELETE'])
@jwt_required()
def delete_user_account():
    """Delete the authenticated user's account."""
    from .models import User
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user['id']).first()

    if not user:
        return jsonify(message="User not found"), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify(message="Account deleted successfully"), 200


from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .db import db

api_bp = Blueprint('api', __name__)

@api_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """Retrieve all tasks for the authenticated user."""
    from .models import Task  # Local import to avoid circular dependency
    current_user = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=current_user['id']).all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'completed': t.completed,
        'created_at': t.created_at,
        'updated_at': t.updated_at
    } for t in tasks]), 200

@api_bp.route('/task/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Retrieve a specific task by ID for the authenticated user."""
    from .models import Task  # Local import to avoid circular dependency
    task = Task.query.get(task_id)
    if task and task.user_id == get_jwt_identity()['id']:
        return jsonify({
            'id': task.id,
            'title': task.title, 
            'completed': task.completed,
            'created_at': task.created_at,
            'updated_at': task.updated_at
        }), 200
    return jsonify(message="Task not found"), 404

@api_bp.route('/task', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task for the authenticated user."""
    from .models import Task  # Local import to avoid circular dependency
    data = request.get_json()
    current_user = get_jwt_identity()

    new_task = Task(
        title=data['title'],
        completed=data.get('completed', False),
        user_id=current_user['id']
    )
    db.session.add(new_task)
    db.session.commit()
    
    return jsonify(message="Task created", task_id=new_task.id), 201

@api_bp.route('/task/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a specific task by ID for the authenticated user."""
    from .models import Task  # Local import to avoid circular dependency
    task = Task.query.get(task_id)
    if task and task.user_id == get_jwt_identity()['id']:
        data = request.get_json()
        task.title = data.get('title', task.title)
        task.completed = data.get('completed', task.completed)
        db.session.commit()
        return jsonify(message="Task updated"), 200
    return jsonify(message="Task not found or unauthorized"), 404

@api_bp.route('/task/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a specific task by ID for the authenticated user."""
    from .models import Task  # Local import to avoid circular dependency
    task = Task.query.get(task_id)
    if task and task.user_id == get_jwt_identity()['id']:
        db.session.delete(task)
        db.session.commit()
        return jsonify(message="Task deleted"), 200
    return jsonify(message="Task not found or unauthorized"), 404

@api_bp.route('/user', methods=['PUT'])
@jwt_required()
def update_user_info():
    """ Update user information for the authenticated user """
    from .models import User
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user['id']).first()
    
    if not user:
        return jsonify(message="User not found"), 404
    
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    
    db.session.commit()
    return jsonify(message="User info updated successfully"), 200

@api_bp.route('/user', methods=['DELETE'])
@jwt_required()
def delete_user_account():
    """Delete the authenticated user's account."""
    from .models import User
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user['id']).first()

    if not user:
        return jsonify(message="User not found"), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify(message="Account deleted successfully"), 200


@api_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_profile_picture():
    """Upload a profile picture for the authenticated user."""
    from .models import User
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user['id']).first()

    if not user:
        return jsonify(message="User not found"), 404

    file = request.files['file']
    if file:
        file_path = f'static/uploads/{file.filename}'  # Save to the static/uploads directory
        file.save(file_path)
        user.profile_picture = file_path
        db.session.commit()
        return jsonify(message="Profile picture uploaded successfully", profile_picture=user.profile_picture), 200

    return jsonify(message="File not provided"), 400

