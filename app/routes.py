import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
from .db import db
from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta
from app.models import Event, User, Task


api_bp = Blueprint('api', __name__)

# Import necessary models

@api_bp.route('/<path:path>', methods=['OPTIONS'])
def handle_preflight(path):
    return jsonify({'status': 'ok'}), 200

@api_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """Retrieve all tasks for the authenticated user."""
    current_user = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=current_user['id']).all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'completed': t.completed,
        'created_at': t.created_at,
        'updated_at': t.updated_at
    } for t in tasks]), 200

@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Retrieve a specific task by ID for the authenticated user."""
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

@api_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task for the authenticated user."""
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

@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a specific task by ID for the authenticated user."""
    task = Task.query.get(task_id)
    if task and task.user_id == get_jwt_identity()['id']:
        data = request.get_json()
        task.title = data.get('title', task.title)
        task.completed = data.get('completed', task.completed)
        db.session.commit()
        return jsonify(message="Task updated"), 200
    return jsonify(message="Task not found or unauthorized"), 404

@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a specific task by ID for the authenticated user."""
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
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user['id']).first()
    
    if not user:
        return jsonify(message="User not found"), 404
    
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    
    db.session.commit()
    return jsonify(message="User info updated successfully"), 200

@api_bp.route('/upload', methods=['POST', 'OPTIONS'])
@jwt_required()
def upload_profile_picture():
    if request.method == 'OPTIONS':
        return '', 200  # Send a blank response with 200 OK for preflight OPTIONS request

    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user['id']).first()

    if not user:
        return jsonify(message="User not found"), 404

    file = request.files.get('file')
    if file:
        file_path = f'static/uploads/{file.filename}'  # Save to the static/uploads directory
        file.save(file_path)
        user.profile_picture = file_path
        db.session.commit()
        return jsonify(message="Profile picture uploaded successfully", profile_picture=user.profile_picture), 200

    return jsonify(message="File not provided"), 400


# --- TIMELINE ROUTES ---

# 1. Get events for a date range (timeline view)
@api_bp.route('/timeline', methods=['GET'])
@jwt_required()
def get_timeline_events():
    """Retrieve events within a 7-day range of the current date."""
    current_user = get_jwt_identity()
    current_date = request.args.get('current_date')  # 'YYYY-MM-DD'
    if not current_date:
        return jsonify({'error': 'Missing current_date parameter'}), 400

    current_date_obj = datetime.strptime(current_date, '%Y-%m-%d')
    start_date = current_date_obj - timedelta(days=7)
    end_date = current_date_obj + timedelta(days=7)

    events = Event.query.filter_by(user_id=current_user['id']).filter(Event.event_date.between(start_date, end_date)).order_by(Event.event_date.asc()).all()

    events_data = [{
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'event_date': event.event_date.strftime('%Y-%m-%d'),
        'created_at': event.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': event.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    } for event in events]

    return jsonify(events_data)

# 2. Create a new event
@api_bp.route('/events', methods=['POST'])
@jwt_required()
def create_event():
    """Create a new event."""
    data = request.json
    current_user = get_jwt_identity()

    if 'title' not in data or 'event_date' not in data:
        return jsonify({'error': 'Title and event_date are required fields'}), 400

    event_date_obj = datetime.strptime(data['event_date'], '%Y-%m-%d')

    new_event = Event(title=data['title'], description=data.get('description', ''), event_date=event_date_obj, user_id=current_user['id'])
    db.session.add(new_event)
    db.session.commit()

    return jsonify({'message': 'Event created successfully', 'event_id': new_event.id}), 201

# 3. Update an event by ID
@api_bp.route('/events/<int:id>', methods=['PUT'])
@jwt_required()
def update_event(id):
    """Update a specific event by ID."""
    data = request.json
    event = Event.query.get_or_404(id)

    # Ensure the user trying to update the event is the creator
    if event.user_id != get_jwt_identity()['id']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Update fields
    event.title = data.get('title', event.title)
    event.description = data.get('description', event.description)
    if 'event_date' in data:
        try:
            event.event_date = datetime.strptime(data['event_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format for event_date, expected YYYY-MM-DD'}), 400

    db.session.commit()
    return jsonify({'message': 'Event updated successfully'})


# 4. Delete an event by ID
@api_bp.route('/events/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_event(id):
    """Delete a specific event by ID."""
    event = Event.query.get_or_404(id)

    if event.user_id != get_jwt_identity()['id']:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(event)
    db.session.commit()

    return jsonify({'message': 'Event deleted successfully'})

